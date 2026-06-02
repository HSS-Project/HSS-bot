import asyncio
import json
from importlib import import_module
import memorization_maker.Read_and_Write as Read_and_Write
import os
import re
import tempfile
from typing import TypedDict
from typing_extensions import NotRequired
from typing import Union
import openpyxl
import random
from io import BytesIO

class QuestionData(TypedDict):
    question: str
    answer: str
    mode: int
    select: NotRequired[list[str]]

class CardData(TypedDict):
    questions: list[QuestionData]
    onwer: list[str]
    sharecode: Union[int, bool]

class answerTypedDict(TypedDict):
    answer: str

class MemorizationData(answerTypedDict):
    memorization: dict[dict[str, CardData]]

class Add:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.base_data:dict = {"memorization":{}, "genre":{}}

    def _strip_code_fence(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def _extract_json_payload(self, text: str):
        text = self._strip_code_fence(text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise
            return json.loads(text[start:end + 1])

    def _normalize_generated_questions(self, payload):
        if isinstance(payload, dict):
            questions = payload.get("questions", [])
        elif isinstance(payload, list):
            questions = payload
        else:
            return []

        normalized = []
        for question in questions:
            if not isinstance(question, dict):
                continue

            mode = question.get("mode")
            if mode is None:
                if isinstance(question.get("select"), list):
                    mode = 1
                elif isinstance(question.get("answer"), list):
                    mode = 2
                else:
                    mode = 0

            try:
                mode = int(mode)
            except (TypeError, ValueError):
                continue

            question_text = str(question.get("question", "")).strip()
            if not question_text:
                continue

            if mode == 0:
                answer = str(question.get("answer", "")).strip()
                if not answer:
                    continue
                normalized.append({"question": question_text, "answer": answer, "mode": 0})
            elif mode == 1:
                select = question.get("select", [])
                if not isinstance(select, list) or len(select) < 2:
                    continue
                select = [str(choice).strip() for choice in select if str(choice).strip()]
                if len(select) < 2:
                    continue

                answer = question.get("answer")
                if isinstance(answer, str) and answer.isdigit():
                    answer = int(answer)
                try:
                    answer = int(answer)
                except (TypeError, ValueError):
                    continue
                if answer < 0 or answer >= len(select):
                    continue

                normalized.append({"question": question_text, "answer": answer, "mode": 1, "select": select})
            elif mode == 2:
                answer = question.get("answer", [])
                if not isinstance(answer, list):
                    continue
                answers = [str(item).strip() for item in answer if str(item).strip()]
                if not answers:
                    continue
                normalized.append({"question": question_text, "answer": answers, "mode": 2})

        return normalized

    async def _extract_pdf_text(self, pdf_path: str) -> str:
        pdf_module = import_module("pypdf")
        reader = pdf_module.PdfReader(pdf_path)
        pages = []
        for index, page in enumerate(reader.pages[:20], start=1):
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            if page_text:
                pages.append(f"--- page {index} ---\n{page_text[:4000]}")
        return "\n\n".join(pages)

    def _generate_questions_with_gemini(self, pdf_path: str, extracted_text: str, api_key: str, max_questions: int, force_mode: int | None = None, ai_instruction: str | None = None):
        from google import genai

        client = genai.Client(api_key=api_key)
        uploaded_pdf = client.files.upload(file=pdf_path)
        prompt = (
            "あなたはPDF教材から暗記問題を作るアシスタントです。"
            "添付されたPDFを読み、問題をJSONのみで返してください。"
            "出力は必ず次の形式にしてください。\n"
            '{"questions":[{"mode":0,"question":"...","answer":"..."},'
            '{"mode":1,"question":"...","select":["...","...","...","..."],"answer":0},'
            '{"mode":2,"question":"...","answer":["..."]}]}'
            f"問題数は最大 {max_questions} 問にしてください。\n"
            "mode 0 は記述式、mode 1 は4択、mode 2 は穴埋めです。\n"
            "選択式は必ず4個の選択肢を入れ、answer は 0 から 3 の整数にしてください。\n"
            "穴埋めは答えを配列で返してください。\n"
            "余計な説明文、Markdown、コードフェンスは返さないでください。\n"
        )
        # 強制モードが指定されている場合は生成ルールを絞る
        if force_mode is not None:
            if force_mode == 1:
                prompt += "\n注意: 生成する問題はすべて選択式(mode 1：4択)のみとしてください。answer は 0 から 3 の整数で返してください。\n"
            elif force_mode == 2:
                prompt += "\n注意: 生成する問題はすべて穴埋め(mode 2)のみとしてください。\n"
            elif force_mode == 0:
                prompt += "\n注意: 生成する問題はすべて記述式(mode 0)のみとしてください。\n"
        # ユーザ指定のAI指令を追記
        if ai_instruction:
            prompt += "\n追加の指示: " + ai_instruction + "\n"
        if extracted_text:
            prompt += "\nPDFから抽出したテキストの補助情報:\n" + extracted_text

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, uploaded_pdf],
        )
        raw_text = getattr(response, "text", "") or ""
        if not raw_text:
            return []

        payload = self._extract_json_payload(raw_text)
        return self._normalize_generated_questions(payload)

    async def generate_questions_from_pdf(self, pdffile, api_key: str, max_questions: int = 50, force_mode: int | None = None, ai_instruction: str | None = None):
        pdf_bytes = await pdffile.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        try:
            extracted_text = await self._extract_pdf_text(temp_path)
            # max_questions の範囲を制限（MAX=100）
            try:
                max_q = int(max_questions)
            except Exception:
                max_q = 50
            if max_q > 100:
                max_q = 100
            if max_q < 1:
                max_q = 1
            questions = await asyncio.to_thread(
                self._generate_questions_with_gemini,
                temp_path,
                extracted_text,
                api_key,
                max_q,
                force_mode,
                ai_instruction,
            )
            return questions
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

    async def add_generated_questions(self, _sharecode, questions):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        if sharecode not in self.base_data["memorization"]:
            return False

        for question in questions:
            record = {"question": question["question"], "answer": question["answer"], "mode": question["mode"]}
            if question["mode"] == 1:
                record["select"] = question["select"]
            self.base_data["memorization"][sharecode]["questions"].append(record)

        await self.rw.write_base(self.base_data)
        return True

    async def init_add(self,user_id:str,title:str,_sharecode):
        num_id = str(user_id)
        sharecode = str(_sharecode)
        self.base_data:dict = await self.rw.load_base()
        # すでにタイトルが存在している場合はFalseを返す
        if title in self.base_data["memorization"].keys():
            return False
        self.base_data["memorization"].setdefault(sharecode, {"title":f"{title}_{sharecode}","questions": [], "onwer":[num_id]})
        await self.rw.write_base(self.base_data)
        return True

    async def add_misson(self,_sharecode,quetion:str,answer:str):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        self.base_data["memorization"][sharecode]["questions"].append({"question":quetion,"answer":answer,"mode":0})
        await self.rw.write_base(self.base_data)

    async def add_misson_select(self,_sharecode,quetion:str,answer,select:list):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        self.base_data["memorization"][sharecode]["questions"].append({"question":quetion,"answer":answer,"mode":1,"select":select})
        await self.rw.write_base(self.base_data)

    async def replace_parentheses(self, source_text: str):
        # ()内のテキストを抽出
        answers:list = re.findall(r'\((.*?)\)', source_text)
        
        # ()内のテキストを①、②、③...に置き換え
        if len(answers) > 5:
            return False, False
        for i, answer in enumerate(answers):
            number = chr(9312 + i)  # 9312はUnicodeで①の値
            source_text = source_text.replace(f'({answer})', f'{number}')
        return source_text, answers
    
    def replace_numbers_with_answers(self,text, answers):
        # 正規表現で番号を探して置き換える
        for i, answer in enumerate(answers):
            number = chr(9312 + i)  # 9312はUnicodeで①の値
            text = text.replace(f'{number}', f'||{answer}||')
        return text
    
    async def add_misson_text(self,_sharecode,text:str):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        text, answers = await self.replace_parentheses(text)
        if text is False or answers is False:return False
        self.base_data["memorization"][sharecode]["questions"].append({"question":text,"answer":answers, "mode":2})
        await self.rw.write_base(self.base_data)
        
    async def add_misson_in_Excel(self,_sharecode,excelfile):
        self.base_data:dict = await self.rw.load_base()
        excel_bytes = await excelfile.read()
        excel_file = BytesIO(excel_bytes)  
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
        sharecode = str(_sharecode)
        row_count = sum(1 for _ in sheet.iter_rows(min_col=1,values_only=True))
        if not row_count > 4:return False
        for row in sheet.iter_rows(min_row=1, values_only=True):
            if row[0] or row[1] or row[2]:
                mode = int(row[2])
                if not isinstance(mode, int):return False
                question = row[0]
                answer = row[1]
                if mode == 0:
                    await self.add_misson(sharecode,question,answer)
                elif mode == 1:
                    select = []
                    if len(row) == 6:
                        select = [row[3],row[4],row[5],row[6]]
                        answer_num = select.index(answer)
                    else:
                        num_rows_max = sheet.max_row
                        random_answer_index = random.randint(0,3)
                        for _ in range(4):
                            while True:
                                random_select = random.randint(1, num_rows_max + 1)
                                cell = sheet.cell(row=random_select, column=2)
                                if cell.value not in select and cell.value is not None:
                                    if not cell.value  == answer:
                                        select.append(cell.value)
                                        break
                        select[random_answer_index] = answer
                        answer_num = select.index(answer)
                    await self.add_misson_select(sharecode,question,answer_num,select)
            elif row[0] and int(row[2]) == 2:
                await self.add_misson_text(sharecode,row[0])
            else:
                print("error")
        await self.rw.write_base(self.base_data)
        return True