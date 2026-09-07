from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

ROOT = Path(__file__).parent
ITEMS = [('SC2691','Hospital / revised blocking','right'),('SC2591','Iron box / after Lula arrives','left'),('SC2215_idle','Earl day / busy','right'),('SC2215_clicked','Earl day / interrupted','right'),('SC2515_idle','Earl night / withdrawn','right'),('SC2515_clicked','Earl night / guarding hand','right'),('SC2615_idle','Liaison / provisional body','right'),('SC2615_clicked','Liaison / cold glance','right')]
ui = Image.open(r'D:/NDC/Assets/Resources/Art/UI/AVG/left_BG.png').convert('RGBA')
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for overlay in [False,True]:
    board = Image.new('RGB',(1640,2200),'#202226')
    draw=ImageDraw.Draw(board)
    for i,(key,label,side) in enumerate(ITEMS):
        im=Image.open(ROOT/(key+'.png')).convert('RGBA')
        if overlay:
            panel=ui.resize((round(im.height*ui.width/ui.height),im.height))
            if side=='right': panel=panel.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            im.alpha_composite(panel,(0 if side=='left' else im.width-panel.width,0))
            im.save(ROOT/(key+'_UI.png'))
        im.thumbnail((800,480))
        x=20+(i%2)*810; y=20+(i//2)*545
        board.paste(im,(x+(800-im.width)//2,y+(480-im.height)//2))
        draw.text((x,y+488),label+(' / UI '+side if overlay else ''),font=font,fill='white')
    board.save(ROOT/('review_UI.png' if overlay else 'review_all.png'))
print(ROOT/'review_all.png')
