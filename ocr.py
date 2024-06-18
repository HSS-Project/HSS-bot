#ライブラリインポート
import pyocr
from PIL import Image, ImageEnhance
import os

#OCRエンジン取得
tools = pyocr.get_available_tools()
tool = tools[0]

#OCRの設定 ※tesseract_layout=6が精度には重要。デフォルトは3
builder = pyocr.builders.TextBuilder(tesseract_layout=6)

#解析画像読み込み(雨ニモマケズ)
img = Image.open('image.png') #他の拡張子でもOK

img_g = img.convert('L') #Gray変換
enhancer= ImageEnhance.Contrast(img_g) #コントラストを上げる
img_con = enhancer.enhance(2.0) #コントラストを上げる

#画像からOCRで日本語を読んで、文字列として取り出す
#言語は日本語(jpn)、ビルダーはテキスト
txt_pyocr = tool.image_to_string(img_con , lang='jpn', builder=builder)
txt_pyocr_vert = tool.image_to_string(img_con , lang='jpn_vert', builder=builder)
txt_pyocr_japanese = tool.image_to_string(img_con , lang='Japanese', builder=builder)
txt_pyocr_japanese_vert = tool.image_to_string(img_con , lang='Japanese_vert', builder=builder)

#半角スペースを消す ※読みやすくするため
txt_pyocr = txt_pyocr.replace(' ', '')
txt_pyocr_vert = txt_pyocr_vert.replace(' ', '')
txt_pyocr_japanese = txt_pyocr_japanese.replace(' ', '')
txt_pyocr_japanese_vert = txt_pyocr_japanese_vert.replace(' ', '')


print(txt_pyocr)
print("\n\n")
print(txt_pyocr_vert)
print("\n\n")
print(txt_pyocr_japanese)
print("\n\n")
print(txt_pyocr_japanese_vert)

