from tkinter import *
from tkinter import _setit as setit
from tkinter import filedialog
from tkinter.messagebox import *
from PIL import Image, ImageDraw, ImageFont, ImageTk
from re import fullmatch, findall, sub

DEFAULT = "- Aucun -"
DEFAULT_TEMPLATE = "Vertical"
DEFAULT_IMAGE = "src/pic/alakir.png"
DEFAULT_NAME = "Al'Akir"
DEFAULT_NAME_SIZE = 72
DEFAULT_NAME_COLOR = DEFAULT
DEFAULT_TYPE = "Seigneur des vents"
DEFAULT_TYPE_SIZE = 60
DEFAULT_TYPE_COLOR = DEFAULT
DEFAULT_NUMERO = ""
DEFAULT_NUMERO_SIZE = 64
DEFAULT_NUMERO_COLOR = DEFAULT
DEFAULT_POWER = ""
DEFAULT_POWER_SIZE = 48
DEFAULT_POWER_COLOR = DEFAULT
DEFAULT_POWER_POSITION = "Gauche du type"
DEFAULT_ANCHOR = (0,0)
DEFAULT_COLOR = DEFAULT
DEFAULT_STRIP_COLOR = DEFAULT
DEFAULT_CONTOUR_COLOR = "Noir"
DEFAULT_FACTION = "Balance"
DEFAULT_SYMBOLE = "- Vide -"
DEFAULT_STAT  = "12"
DEFAULT_PERSO = "7"
DEFAULT_MODE = "Normal"
MAX_SYMBOLE = 5
ALL_STAT = ["weapon_skill", "strength", "speed", "bravery", "intelligence", "toughness"]
FONT_POISON = "src/stats/m/"
HELP_TEXT = "Cochez cette case pour que le panneau de conseils continue à vous donner des conseils comme celui-ci.\nDécochez-la pour être tranquille."
ILLUS_X = 0
ILLUS_Y = 0
ILLUS_NORMAL = 1
ILLUS_AUCUNE = 2
ILLUS_CONTOUR = 3
ILLUS_DEP_ZER = 4
ILLUS_DEP_DEB = 5
ILLUS_DEP_MID = 6
ILLUS_DEP_FIN = 7
CARD_WIDTH  = 1500
CARD_HEIGHT = 2300
FACTION_WIDTH  = 541
FACTION_HEIGHT = 612
CARD_DISPLAY_RATIO = 4
MOUSE_WHEEL_TICK = 120
FILE_COLOR = "color.txt"

def zoom_to_string(zoom):
  if int(zoom*10000)%100 == 0:
    return str(round(100*zoom))
  return str(round(100*zoom,2))

def stat_to_string(stat):
  wordList = stat.split("_")
  answer = ""
  for word in wordList:
    answer += word.capitalize() + " "
  return answer

def centered_text(drawing, rectangle, text, font=None, color="black", outline=False, ignoreDescender=True):
  W, H = rectangle[1][0] - rectangle[0][0], rectangle[1][1] - rectangle[0][1]
  X, Y = rectangle[0][0], rectangle[0][1]
  w, h = drawing.textsize(text, font=font)
  if ignoreDescender:
    _, h = drawing.textsize('E', font=font)
  x, y = X + (W-w)//2, Y + (H-h)//2
  if outline:
    drawing.text((x-1, y), text, font=font, fill="black")
    drawing.text((x+1, y), text, font=font, fill="black")
    drawing.text((x, y-1), text, font=font, fill="black")
    drawing.text((x, y+1), text, font=font, fill="black")
  drawing.text((x, y), text, font=font, fill=color)
  return [(x,y),(x+w,y+h)]

def rjust_text(drawing, X, Y, text, font=None, color="black", spacing=0):
  w, _ = drawing.textsize(text, font=font)
  x, y = X-w-spacing, Y
  drawing.text((x, y), text, font=font, fill=color)

def drawStat(img, rectangle, path, number, ratio=1, compactHalf=True):
  reg = "^([Pp]?) *([0-9]*)([,.]5| *1/2)?$"
  if fullmatch(reg, number):
    args = (sub(reg, "\\1\n\\2\n\\3", number).split('\n'))
    if   args[1] == "11": spacing = 30
    elif args[1] == "12": spacing = 25
    elif args[1] == "10": spacing = 18
    elif args[1] == "1": spacing = 25
    else: spacing = 15
    try:
      picture = [None]*len(args)
      if args[0]: picture[0] = Image.open("%s/p.png" % path)
      if args[1]: picture[1] = Image.open("%s/%s.png" % (path, args[1]))
      if args[2]: picture[2] = Image.open("%s/1%s2.png" % (path, "_" if compactHalf else "/"))
      W, H = rectangle[1][0] - rectangle[0][0], rectangle[1][1] - rectangle[0][1]
      X, Y = rectangle[0][0], rectangle[0][1]
      w, h = 0, 0
      for i in range(len(picture)):
        pic = picture[i]
        if pic:
          wt, ht = pic.size
          w += wt
          if i == 0: w += spacing-10
          if i == 1 and picture[2]: w += spacing
          h = max(h, ht)
      fullPicture = Image.new('RGBA', (w, h), (0,0,0,0))
      wa = 0
      for i in range(len(picture)):
        pic = picture[i]
        if pic:
          wt, ht = pic.size
          fullPicture.paste(pic, (wa,(h-ht)//2), pic)
          wa += wt
          if i == 0: wa += spacing-10
          if i == 1 and picture[2]: wa += spacing
      fullPicture.thumbnail((w//ratio, h//ratio), Image.BILINEAR)
      w, h = fullPicture.size
      x, y = X + (W-w)//2, Y + (H-h)//2
      img.paste(fullPicture, (x, y), fullPicture)
      for pic in picture:
        if pic: pic.close()
    except:
      for pic in picture:
        try: pic.close()
        except: pass

def symbole_name(string):
  return sub(' \(.*\)','',string)
  
def symbole_number(string):
  l = findall('\(.*\)',string)
  if l: return l[-1][1:-1]
  else: return ''

class CustomDialog(Toplevel):

  def __init__(self, parent, title = None):

    Toplevel.__init__(self, parent)
    self.transient(parent)
    self.resizable(False, False)

    if title:
      self.title(title)

    self.parent = parent
    self.result = None

    body = Frame(self)
    body.pack(padx=5, pady=5)
    Label(body, text="Puissance :").pack(side=LEFT, padx=(0,5))
    self.e = Entry(body, width=10)
    self.e.pack(side=LEFT)

    self.initial_focus = self.e
    
    self.buttonbox()
    self.grab_set()

    self.protocol("WM_DELETE_WINDOW", self.cancel)
    self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
    self.initial_focus.focus_set()
    self.wait_window(self)

  def buttonbox(self):
    box = Frame(self)

    w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
    w.pack(side=LEFT, padx=5, pady=5)
    w = Button(box, text="Annuler", width=10, command=self.cancel)
    w.pack(side=LEFT, padx=5, pady=5)

    self.bind("<Return>", self.ok)
    self.bind("<Escape>", self.cancel)

    box.pack()

  def ok(self, event=None):

    if not self.validate():
      self.initial_focus.focus_set() # put focus back
      return

    self.withdraw()
    self.update_idletasks()

    self.apply()
    self.cancel()

  def cancel(self, event=None):

    self.parent.focus_set()
    self.destroy()

  def validate(self):
    return 1 # override

  def apply(self):
    self.result = self.e.get()

class ResetDialog(Toplevel):

  def __init__(self, parent, title = None):

    Toplevel.__init__(self, parent)
    self.transient(parent)
    self.resizable(False, False)

    if title:
      self.title(title)

    self.parent = parent
    self.result = False

    body = Frame(self)
    body.pack(padx=5, pady=5)
    Label(body, text="Voulez-vous vraiment supprimer cette carte\net réinitialiser tous les paramètres ?").pack()

    self.initial_focus = self
    
    self.buttonbox()
    self.grab_set()

    self.protocol("WM_DELETE_WINDOW", self.cancel)
    self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
    self.initial_focus.focus_set()
    self.wait_window(self)

  def buttonbox(self):
    box = Frame(self)

    w = Button(box, text="Oui, tout supprimer", width=15, command=self.ok)
    w.pack(side=LEFT, padx=5, pady=5)
    w = Button(box, text="Non, annuler", width=15, command=self.cancel, default=ACTIVE)
    w.pack(side=LEFT, padx=5, pady=5)
    
    self.bind("<Return>", self.cancel)
    self.bind("<Escape>", self.cancel)

    box.pack()

  def ok(self, event=None):

    if not self.validate():
      self.initial_focus.focus_set() # put focus back
      return

    self.withdraw()
    self.update_idletasks()

    self.apply()
    self.cancel()

  def cancel(self, event=None):

    self.parent.focus_set()
    self.destroy()

  def validate(self):
    return 1 # override

  def apply(self):
    self.result = True
    
class Carte():
  def __init__(self):
    self.color_dict = {}
    self.computeColor()
    
    self.position_dict = {
      DEFAULT_POWER_POSITION: 0,
      "Gauche du nom": 1,
    }
    
    self.mode_dict = {
      DEFAULT_MODE: ILLUS_NORMAL,
      "Déborde s/s le texte": ILLUS_DEP_DEB,
      "Déborde s/s symbole": ILLUS_DEP_MID,
      "Déborde s/s tout": ILLUS_DEP_ZER,
      "Déborde sur tout": ILLUS_DEP_FIN,
      "Contour seul": ILLUS_CONTOUR,
      "Pas d'illustration": ILLUS_AUCUNE,
    }
    
    self.faction_dict = {
      "- Vide -" : "vide",
      "Balance" : "aism",
      "Loi" : "loi",
      "Chaos" : "ko",
    }
    
    self.symbole_dict = {
      DEFAULT_SYMBOLE : {"name": "vide", "center": (187,187)},
      
      "Arc" : {"name": "arc", "center": (200,198)},
      "Casque" : {"name": "casque", "center": (194,204)},
      "Couronne" : {"name": "couronne", "center": (192,215)},
      "Crocs" : {"name": "crocs", "center": (194,192)},
      "Épée" : {"name": "épée", "center": (193,211)},
      "Étendard" : {"name": "etendard", "center": (196,197)},
      "Flamme" : {"name": "flamme", "center": (210,230)},
      "Hurlante" : {"name": "hurlante", "center": (208,241)},
      "Medic" : {"name": "médic", "center": (189,189)},
      "Œil" : {"name": "oeil", "center": (230,235)},
      
      "Collision" : {"name": "collision", "center": (205,203)},
      "Écraser" : {"name": "ecras", "center": (191,193)},
      "Fanatique" : {"name": "fanat", "center": (189,191)},
      "Fuite" : {"name": "fuite", "center": (202,204)},
      "Gel" : {"name": "gel", "center": (184,184)},
      "Killer" : {"name": "killer", "center": (197,201)},
      "Nécromancie" : {"name": "necro", "center": (194,195)},
      "Poison" : {"name": "poison", "center": (192,192), "custom":
        {"text_center" : (195,50), "text_ratio" : 2}
      },
      "Raz de marée" : {"name": "razdemaree", "center": (207,202)},
      "Tornade" : {"name": "tornade", "center": (197,198)},
      
      "Aveuglement" : {"name": "aveuglement", "center": (195,192)},
      "Bâton magique" : {"name": "batonmag", "center": (183,183)},
      "Chance" : {"name": "chance", "center": (183,179)},
      "Démon" : {"name": "demon", "center": (171,171)},
      "Élite" : {"name": "elite", "center": (199,671)},
      "Nécromancien" : {"name": "mnecro", "center": (178,174)},
      "Portail" : {"name": "portail", "center": (183,183)},
      "Prescience" : {"name": "boulepresc", "center": (186,203), "custom":
        {"text_center" : (189,143), "text_ratio" : 1}
      },
      "Sablier" : {"name": "sablier", "center": (186,186)},
      
      "Blaster" : {"name": "blaster", "center": (188,193)},
      "Laser" : {"name": "laser", "center": (193,194)},
      "Paralyseur" : {"name": "paralyseur", "center": (181,183)},
      "Sabre bleu" : {"name": "sablleu", "center": (185,185)},
      "Sabre rouge" : {"name": "sabrouj", "center": (185,185)},
      
      "★" : {"name": "boule1", "center": (182,182)},
      "★★" : {"name": "boule2", "center": (194,189)},
      "★★★" : {"name": "boule3", "center": (187,183)},
      "★★★★" : {"name": "boule4", "center": (184,185)},
    }
    
    self.symbole_blueprint = [
      [1],
      [],
      ["Orignal", 10],
      ["Nouveau", 10],
      ["Spécial", 9],
      ["Star Wars", 5],
      ["Dragon Ball", 4],
    ]
    
    self.template_dict = {
    "Vertical" : {
      "name_rectangle"   : [(550,104), (1400,184)],
      "type_rectangle"   : [(550,204), (1400,284)],
      "numero_rectangle" : [(412,171), (476,235)],
      "power_rectangle" : [(536,76), (700,188)],
      "faction_coo"      : (81, 1542),
      "fond" : "src/template/patronbloi.png",
      "contour" : "src/template/contour_patronbloi.png",
      "contour_unset"     : "src/template/contour_unset_patronbloi.png",
      "masque_contour"    : "src/template/masque_contour_patronbloi.png",
      "masque_couleur"    : "src/template/masque_couleur_patronbloi.png",
      "masque_bande"      : "src/template/masque_bande_patronbloi.png",
      "masque_bande_full" : "src/template/masque_bande_full_patronbloi.png",
      "stats_text"        : "src/template/texte_patronbloi.png",
      "stats_path" : "src/stats/n/",
      "stats" : {
        "weapon_skill" : [(124,244),(519,405)],
        "strength"     : [(125,444),(520,639)],
        "speed"        : [(126,677),(521,871)],
        "bravery"      : [(127,907),(522,1105)],
        "intelligence" : [(128,1141),(523,1337)],
        "toughness"    : [(130,1374),(525,1570)],
        },
      "chance_coo"   : (542,305),
      "charisme_coo" : (1139,315),
      "chance_rectangle"   : [(552,352),(725,440)],
      "charisme_rectangle" : [(1129,362),(1348,450)],
      "chance_path"   : "src/stats/m/",
      "charisme_path" : "src/stats/m/",
      "symbole_coo" : {
        1 : [(960,1933)],
        2 : [(807,1933), (1237,1933)],
        3 : [(710,1746), (1244,1746), (978,1950)],
        4 : [(693,1771), (1095,1771), (855,1965), (1257,1965)],
        5 : [(780,1974), (1196,1974), (678,1742), (1252,1742), (980,1856)],
        },
      },
    "Horizontal" : {
      "name_rectangle" : [(56,97), (1457,187)],
      "type_rectangle" : [(56,187), (1457,277)],
      "numero_rectangle" : [(128,310), (260,380)],
      "power_rectangle" : [(536,76), (700,188)],
      "faction_coo"    : (69, 1572),
      "fond" : "src/template/patronvaism.png",
      "contour" : "src/template/contour_patronvaism.png",
      "contour_unset"     : "src/template/contour_unset_patronvaism.png",
      "masque_contour"    : "src/template/masque_contour_patronvaism.png",
      "masque_couleur"    : "src/template/masque_couleur_patronvaism.png",
      "masque_bande"      : "src/template/masque_bande_patronvaism.png",
      "masque_bande_full" : "src/template/masque_bande_full_patronvaism.png",
      "stats_text"        : "src/template/texte_patronvaism.png",
      "stats_path" : "src/stats/m/",
      "stats" : {
        "weapon_skill" : [(132,469),(266,642)],
        "strength"     : [(333,468),(486,643)],
        "speed"        : [(574,469),(673,644)],
        "bravery"      : [(767,470),(908,645)],
        "intelligence" : [(948,470),(1161,645)],
        "toughness"    : [(1185,470),(1361,646)],
        },
      "chance_coo"   : (103,689),
      "charisme_coo" : (1178,699),
      "chance_rectangle"   : [(113,736),(286,824)],
      "charisme_rectangle" : [(1187,746),(1370,834)],
      "chance_path"   : "src/stats/m/",
      "charisme_path" : "src/stats/m/",
      "symbole_coo" : {
        1 : [(965,1940)],
        2 : [(794,1940), (1201,1940)],
        3 : [(733,1885), (1231,1710), (1049,1967)],
        4 : [(670,1791), (1072,1791), (832,1992), (1234,1992)],
        5 : [(780,2004), (1196,2004), (678,1772), (1212,1702), (970,1876)],
        },
      },
    }
    
    self.template = DEFAULT_TEMPLATE
    self.name = DEFAULT_NAME
    self.nameSize = DEFAULT_NAME_SIZE
    self.nameColor = self.color_dict[DEFAULT_NAME_COLOR]
    self.type = DEFAULT_TYPE
    self.typeSize = DEFAULT_TYPE_SIZE
    self.typeColor = self.color_dict[DEFAULT_TYPE_COLOR]
    self.numero = DEFAULT_NUMERO
    self.numeroSize = DEFAULT_NUMERO_SIZE
    self.numeroColor = self.color_dict[DEFAULT_NUMERO_COLOR]
    self.power = DEFAULT_POWER
    self.powerSize = DEFAULT_POWER_SIZE
    self.powerColor = self.color_dict[DEFAULT_POWER_COLOR]
    self.powerPosition = self.position_dict[DEFAULT_POWER_POSITION]
    self.color = self.color_dict[DEFAULT_COLOR]
    self.stripColor = self.color_dict[DEFAULT_STRIP_COLOR]
    self.contourColor = DEFAULT_CONTOUR_COLOR
    self.faction = self.faction_dict[DEFAULT_FACTION]
    self.symboleList = []
    self.defaultAnchor = DEFAULT_ANCHOR
    self.anchor = self.defaultAnchor
    self.illusX = ILLUS_X
    self.illusY = ILLUS_Y
    self.cardWidth = CARD_WIDTH
    self.cardHeight = CARD_HEIGHT
    self.cardDisplayRatio = CARD_DISPLAY_RATIO
    self.zoom = 1.0
    self.illusMode = self.mode_dict[DEFAULT_MODE]
    self.showIllus = True
    self.showOutline = False
    self.chooseFraction = True
    
    self.illustration = Image.open(DEFAULT_IMAGE)
    if self.illustration.mode == "RGB":
      a_channel = Image.new('L', self.illustration.size, 255)
      self.illustration.putalpha(a_channel)
    
    self.faction_symbol = {}
    self.preview_faction_symbol = {}
    for faction in self.faction_dict:
      faction_id = self.faction_dict[faction]
      self.faction_symbol[faction_id] = Image.open("src/faction/%s.png" % faction_id)
      self.preview_faction_symbol[faction_id] = self.faction_symbol[faction_id].resize((FACTION_WIDTH // self.cardDisplayRatio, FACTION_HEIGHT // self.cardDisplayRatio), Image.BILINEAR)
    
    self.stats = {
      "weapon_skill" : DEFAULT_STAT,
      "strength"     : DEFAULT_STAT,
      "speed"        : DEFAULT_STAT,
      "bravery"      : DEFAULT_STAT,
      "intelligence" : DEFAULT_STAT,
      "toughness"    : DEFAULT_STAT,
      }
    
    self.chance   = DEFAULT_PERSO
    self.charisme = DEFAULT_PERSO
    
    self.fond    = None
    self.contour = None
    self.contour_unset     = None
    self.masque_contour    = None
    self.masque_couleur    = None
    self.masque_bande      = None
    self.masque_bande_full = None
    self.stats_text        = None
    forme_chance   = None
    forme_charisme = None
    self.contour_w = None
    self.contour_h = None
    self.preview_contour = None
    self.preview_contour_unset = None
    self.preview_fond = None
    self.preview_masque_contour = None
    self.preview_masque_couleur = None
    self.preview_masque_bande   = None
    self.preview_stats_text     = None
    self.preview_forme_chance   = None
    self.preview_forme_charisme = None
    self.update_photo()
  
  def picturize(self, display = True, illusOnly = False):
  
    if display:
      def px(x): return round(x / self.cardDisplayRatio)
      def up(x): return round(x)
      def upa(x): return (round(x[0]), round(x[1]))
    else:
      def px(x): return round(x)
      def up(x): return round(x * self.cardDisplayRatio)
      def upa(x): return (round(x[0] * self.cardDisplayRatio), round(x[1] * self.cardDisplayRatio))
    
    def pxa(x): return [(px(x[0][0]), px(x[0][1])), (px(x[1][0]), px(x[1][1]))]
    def pxc(x): return (px(x[0]), px(x[1]))
    
    ratio = self.cardDisplayRatio if display else 1
    
    img = Image.new('RGBA', (px(self.cardWidth), px(self.cardHeight)), (255,255,255,255))
    drawing = ImageDraw.Draw(img)
    
    ########## Background ##########
    
    # Fond
    if display:
      img.paste(self.preview_fond, (0,0), self.preview_fond)
    else:
      img.paste(self.fond, (0,0), self.fond)
      
    # Couleur de Fond
    if self.color != (0,0,0,0):
      colorPicture = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), self.color)
      if display:
        img.paste(colorPicture, (0,0), self.preview_masque_couleur)
      else:
        img.paste(colorPicture, (0,0), self.masque_couleur)
    
    # Bandes
    if self.stripColor != (0,0,0,0) and self.illusMode != ILLUS_DEP_ZER:
      stripPicture = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), self.stripColor)
      if display:
        img.paste(stripPicture, (0,0), self.preview_masque_bande)
      else:
        img.paste(stripPicture, (0,0), self.masque_bande)
    
    ########## Sous-illustration ##########

    # Illustration
    if self.illusMode in [ILLUS_DEP_DEB,ILLUS_DEP_ZER]:
      illus = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), (255,255,255,0))
      self.pic_contour(illus, display)
      img.paste(illus, (px(self.illusX), px(self.illusY)), illus)
      
      # Personnalité
      if self.chance:
        chance = self.preview_forme_chance if display else self.forme_chance
        img.paste(chance, pxc(self.getTemplateInfo("chance_coo")), chance) 
      if self.charisme:
        charisme = self.preview_forme_charisme if display else self.forme_charisme
        img.paste(charisme, pxc(self.getTemplateInfo("charisme_coo")), charisme)
        
      illus = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), (255,255,255,0))
      self.pic_illus(illus, up, upa)
      img.paste(illus, (px(self.illusX), px(self.illusY)), illus)
      
      # Texte de stats
      if display:
        img.paste(self.preview_stats_text, (0,0), self.preview_stats_text)
      else:
        img.paste(self.stats_text, (0,0), self.stats_text)
    
    ########## Text ##########
  
    font = ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf', px(self.nameSize), layout_engine=ImageFont.LAYOUT_BASIC)
    rectangle = pxa(self.getTemplateInfo("name_rectangle"))
    color = self.nameColor if self.nameColor != (0,0,0,0) else (0,0,0,255)
    # drawing.rectangle(rectangle, fill=self.color)
    ((x_nom,y_nom),(_,_)) = centered_text(drawing, rectangle, self.name, font=font, color=color, outline=self.showOutline)
    
    font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', px(self.typeSize), layout_engine=ImageFont.LAYOUT_BASIC)
    rectangle = pxa(self.getTemplateInfo("type_rectangle"))
    color = self.typeColor if self.typeColor != (0,0,0,0) else (0,0,0,255)
    # drawing.rectangle(rectangle, fill=self.color)
    ((x_type,y_type),(_,_)) = centered_text(drawing, rectangle, self.type, font=font, color=color, outline=self.showOutline)
    
    font = ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf', px(self.numeroSize), layout_engine=ImageFont.LAYOUT_BASIC)
    rectangle = pxa(self.getTemplateInfo("numero_rectangle"))
    color = self.numeroColor if self.numeroColor != (0,0,0,0) else (0,0,0,255)
    centered_text(drawing, rectangle, self.numero, font=font, color=color)    
    
    if self.powerPosition == 0: x,y = x_type,y_type
    elif self.powerPosition == 1: x,y = x_nom,y_nom
    else: x,y=0,0
    font = ImageFont.truetype('C:/Windows/Fonts/timesbd.ttf', px(self.powerSize), layout_engine=ImageFont.LAYOUT_BASIC)
    color = self.powerColor if self.powerColor != (0,0,0,0) else (0,0,0,255)
    rjust_text(drawing, x, y, self.power, font=font, color=color, spacing = px(20))
    
    ########## Stats ##########
    
    for stat in self.getTemplateInfo("stats"):
      rectangle = self.getTemplateSubInfo("stats",stat)
      drawStat(img, pxa(rectangle), self.getTemplateInfo("stats_path"), self.stats[stat], ratio=ratio, compactHalf=self.chooseFraction)
    
    ########## Illustration ##########
    
    if self.illusMode not in [ILLUS_AUCUNE, ILLUS_DEP_DEB, ILLUS_DEP_ZER]:
      illus = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), (255,255,255,0))
      if self.illusMode == ILLUS_NORMAL:
        self.pic_illus(illus, up, upa)
        self.pic_contour(illus, display)
      elif self.illusMode == ILLUS_DEP_MID:
        self.pic_contour(illus, display)
        self.pic_illus(illus, up, upa)
      elif self.illusMode in [ILLUS_CONTOUR, ILLUS_DEP_FIN]:
        self.pic_contour(illus, display)
      img.paste(illus, (px(self.illusX), px(self.illusY)), illus)
    
    ########## Symboles ##########
    
    # Bandes complètes
    if self.stripColor != (0,0,0,0) and self.illusMode == ILLUS_DEP_ZER:
      stripPicture = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), self.stripColor)
      if display:
        img.paste(stripPicture, (0,0), self.preview_masque_bande_full)
      else:
        img.paste(stripPicture, (0,0), self.masque_bande_full)
    
    # Symboles
    self.drawSymboles(img, self.symboleList, ratio_function = pxc, ratio_function_a = pxa, ratio = ratio, display = display)
    
    # Personnalité
    if self.chance and self.illusMode != ILLUS_DEP_DEB:
      chance = self.preview_forme_chance if display else self.forme_chance
      img.paste(chance, pxc(self.getTemplateInfo("chance_coo")), chance)
    rectangle = self.getTemplateInfo("chance_rectangle")
    drawStat(img, pxa(rectangle), self.getTemplateInfo("chance_path"), self.chance, ratio=ratio, compactHalf=self.chooseFraction)
    
    if self.charisme and self.illusMode != ILLUS_DEP_DEB:
      charisme = self.preview_forme_charisme if display else self.forme_charisme
      img.paste(charisme, pxc(self.getTemplateInfo("charisme_coo")), charisme)
    rectangle = self.getTemplateInfo("charisme_rectangle")
    drawStat(img, pxa(rectangle), self.getTemplateInfo("charisme_path"), self.charisme, ratio=ratio, compactHalf=self.chooseFraction)
    
    # Faction
    factionPicture = self.getFactionPhoto(display)
    img.paste(factionPicture, pxc(self.getTemplateInfo("faction_coo")), factionPicture)
    
    ########## Sur-illustration ##########
    
    if self.illusMode == ILLUS_DEP_FIN:
      illus = Image.new('RGBA', (px(self.contour_w), px(self.contour_h)), (255,255,255,0))
      self.pic_illus(illus, up, upa)
      img.paste(illus, (px(self.illusX), px(self.illusY)), illus)
    
    return img
  
  def pic_contour(self, illus, display):
    if display:
      preview_contour = self.preview_contour if self.contourColor == "Noir" else self.preview_contour_unset
      illus.paste(preview_contour, (0,0), self.preview_masque_contour)
    else:
      contour = self.contour if self.contourColor == "Noir" else self.contour_unset
      illus.paste(contour, (0,0), self.masque_contour)
  
  def pic_illus(self, illus, up, upa):
    if self.zoom >= 1: # avoid resizing the whole picture when zooming in
      rectangle = (
        (- self.anchor[0]/self.zoom),
        (- self.anchor[1]/self.zoom),
        ((- self.anchor[0] + self.contour_w)/self.zoom),
        ((- self.anchor[1] + self.contour_h)/self.zoom),
      )
      temp = self.illustration.crop(rectangle)
      w, h = temp.size
      temp = temp.resize((up(w*self.zoom), up(h*self.zoom)), Image.BILINEAR)
      illus.paste(temp, (0,0), temp)
    else:
      w, h = self.illustration.size
      temp = self.illustration.resize((up(w*self.zoom), up(h*self.zoom)), Image.BILINEAR)
      illus.paste(temp, upa(self.anchor), temp)
  
  def centeringZoom(self, center_x, center_y, ratio):
    x, y = self.anchor
    old_zoom = self.zoom
    # if event.delta > 0: # zoom
    # if event.delta < 0: # dézoom
    self.zoom *= ratio
    self.zoom = round(self.zoom, 4)
    x = round(x + (center_x - self.illusX / self.cardDisplayRatio - x) * (1 - self.zoom/old_zoom))
    y = round(y + (center_y - self.illusY / self.cardDisplayRatio - y) * (1 - self.zoom/old_zoom))
    self.anchor = (x,y)
  
  def getNewZoom(self, zoom):
    try:
      new_zoom = round(float(zoom)/100,4)
      assert new_zoom >= 0.001
      return new_zoom
    except:
      return self.zoom
  
  def getTemplateInfo(self, info):
    return self.template_dict[self.template][info]
  
  def getTemplateSubInfo(self, info, subinfo):
    return self.template_dict[self.template][info][subinfo]
  
  def getFactionPhoto(self, display):
    if display:
      return self.preview_faction_symbol[self.faction]
    else:
      return self.faction_symbol[self.faction]
  
  def computeColor(self):
    self.color_dict[DEFAULT] = (0,0,0,0)
    with open(FILE_COLOR, 'r') as f:
      for x in f:
        try:
          assert x[0] == '#'
          hexValue = (int(x[1:3],16),int(x[3:5],16),int(x[5:7],16),255)
          colorName = x[8:].replace("\n", "")
          self.color_dict[colorName] = hexValue
        except:
          pass
  
  def drawSymboles(self, img, symboleList, ratio_function = lambda x: x, ratio_function_a = lambda x: x, ratio = 1, display = True):
    number_of_symbol = len(symboleList)
    for i in range(number_of_symbol):
      symbole = symbole_name(symboleList[i])
      number  = symbole_number(symboleList[i])
      try:
        with Image.open("src/symbole/%s.png" % self.symbole_dict[symbole]["name"]) as picture:
          cX, cY = self.getTemplateInfo("symbole_coo")[number_of_symbol][i]
          cx, cy = self.symbole_dict[symbole]["center"]
          x, y = cX - cx, cY - cy
          w, h = picture.size
          if display:
            picture = picture.resize((w // self.cardDisplayRatio, h // self.cardDisplayRatio), Image.BILINEAR)
          img.paste(picture, ratio_function((x, y)), picture)
          if number:
            xt, yt = self.symbole_dict[symbole]["custom"]["text_center"]
            r = self.symbole_dict[symbole]["custom"]["text_ratio"]
            drawStat(img, ratio_function_a([(x+xt,y+yt),(x+xt,y+yt)]), FONT_POISON, number, ratio=ratio*r, compactHalf=self.chooseFraction)
      except:
        pass
  
  def update_photo(self):
    self.fond    = Image.open(self.getTemplateInfo("fond"))
    self.contour = Image.open(self.getTemplateInfo("contour"))
    self.contour_unset = Image.open(self.getTemplateInfo("contour_unset"))
    self.masque_contour = Image.open(self.getTemplateInfo("masque_contour"))
    self.masque_couleur = Image.open(self.getTemplateInfo("masque_couleur"))
    self.masque_bande = Image.open(self.getTemplateInfo("masque_bande"))
    self.masque_bande_full = Image.open(self.getTemplateInfo("masque_bande_full"))
    self.stats_text   = Image.open(self.getTemplateInfo("stats_text"))
    self.forme_chance   = Image.open("src/extra/chance.png")
    self.forme_charisme = Image.open("src/extra/charisme.png")
    self.contour_w, self.contour_h = self.contour.size
    self.preview_contour = self.contour.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_contour_unset = self.contour_unset.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_fond = self.fond.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_masque_contour    = self.masque_contour.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_masque_couleur    = self.masque_couleur.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_masque_bande      = self.masque_bande.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_masque_bande_full = self.masque_bande_full.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    self.preview_stats_text        = self.stats_text.resize((self.contour_w // self.cardDisplayRatio, self.contour_h // self.cardDisplayRatio), Image.BILINEAR)
    w, h = self.forme_chance.size
    self.preview_forme_chance   = self.forme_chance.resize((w // self.cardDisplayRatio, h // self.cardDisplayRatio), Image.BILINEAR)
    w, h = self.forme_charisme.size
    self.preview_forme_charisme = self.forme_charisme.resize((w // self.cardDisplayRatio, h // self.cardDisplayRatio), Image.BILINEAR)

class Interface(Frame):

  def __init__(self, fenetre, **kwargs):
    Frame.__init__(self, fenetre, **kwargs)
    self.pack()
    
    ########## Variables ##########
    
    self.mouseWheelTick = MOUSE_WHEEL_TICK
    self.lazy = False
    self.carte = Carte()
    self.photo = ImageTk.PhotoImage(self.carte.picturize())
    self.availableColor    = [key for key in self.carte.color_dict]
    self.availablePosition = [key for key in self.carte.position_dict]
    self.availableTemplate = [key for key in self.carte.template_dict]
    self.availableFaction  = [key for key in self.carte.faction_dict]
    self.availableSymbole  = [key for key in self.carte.symbole_dict]
    self.availableMode     = [key for key in self.carte.mode_dict]
    self.symboleBlueprint  = self.carte.symbole_blueprint
    self.colorName = StringVar(self)
    self.colorName.set(DEFAULT_NAME_COLOR)
    self.colorType = StringVar(self)
    self.colorType.set(DEFAULT_TYPE_COLOR)
    self.colorNumero = StringVar(self)
    self.colorNumero.set(DEFAULT_NUMERO_COLOR)
    self.colorPower = StringVar(self)
    self.colorPower.set(DEFAULT_POWER_COLOR)
    self.positionPower = StringVar(self)
    self.positionPower.set(DEFAULT_POWER_POSITION)
    self.color = StringVar(self)
    self.color.set(DEFAULT_COLOR)
    self.colorStrip = StringVar(self)
    self.colorStrip.set(DEFAULT_STRIP_COLOR)
    self.contourColor = StringVar(self)
    self.contourColor.set("Noir")
    self.faction = StringVar(self)
    self.faction.set(DEFAULT_FACTION)
    self.template = StringVar(self)
    self.template.set(DEFAULT_TEMPLATE)
    self.addSymbole = StringVar(self)
    self.addSymbole.set(DEFAULT_SYMBOLE)
    self.modeIllus = StringVar()
    self.modeIllus.set(DEFAULT_MODE)
    self.showIllus = IntVar()
    self.showIllus.set(1)
    self.showOutline = IntVar()
    self.showOutline.set(0)
    self.showTip = IntVar()
    self.showTip.set(0)
    self.chooseFraction = IntVar()
    self.chooseFraction.set(1)
    self.anchorLast = (0,0)
    
    ########## Cadre d'image ##########
    
    self.pictureCadre = Frame(self, borderwidth=2, relief=GROOVE)
    self.pictureCadre.pack(side=LEFT, padx=(10,5), pady=(8,5))
    
    self.canvas = Canvas(self.pictureCadre, width=self.carte.cardWidth//self.carte.cardDisplayRatio , height=self.carte.cardHeight//self.carte.cardDisplayRatio, borderwidth=0, relief=RIDGE)
    self.canvas.configure(background="white")
    self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
    self.canvas.pack(side=LEFT, padx=2, pady=2)

    ########## Cadre d'édition ##########
    
    self.editCadre = Frame(self)
    self.editCadre.pack(side=TOP)
    self.editCadre1 = Frame(self.editCadre)
    self.editCadre1.pack(side=LEFT, padx=5)
    self.editCadre2 = Frame(self.editCadre)
    self.editCadre2.pack(side=LEFT, padx=(0,5))
    self.editCadre3 = Frame(self.editCadre)
    self.editCadre3.pack(side=LEFT, padx=(0,5))

    self.cadre_nom(self.editCadre1, pady=5)
    self.cadre_template(self.editCadre1)
    self.cadre_symbole(self.editCadre1)
    
    self.cadre_type(self.editCadre2, pady=5)
    self.cadre_stat(self.editCadre2)
    self.cadre_perso(self.editCadre2)
    self.cadre_image(self.editCadre2)
    
    self.cadre_numero(self.editCadre3, pady=5)
    self.cadre_power(self.editCadre3)
    self.cadre_option(self.editCadre3)
    self.cadre_save(self.editCadre3)
    
    ########## Cadre d'aide ##########
    
    self.helpCadre = LabelFrame(self, text="Conseils", borderwidth=2, relief=GROOVE)
    self.helpCadre.pack(side=TOP, padx=(0,5), pady=(0,10))
    
    self.entryHelp = Text(self.helpCadre, width=105, height=3, wrap=WORD)
    self.entryHelp.configure(font=('segoe ui', 9))
    self.entryHelp.configure(state=DISABLED)
    self.entryHelp.pack(padx=6, pady=(3,5))
    
    ########## Contrôles ##########
    
    self.canvas.bind('<Button-1>', self.init_update_anchor)
    self.canvas.bind('<B1-Motion>', self.anchor_move)
    self.canvas.bind('<MouseWheel>', self.anchor_zoom)
    self.entryZoom.bind('<Up>',   self.zoom_increase)
    self.entryZoom.bind('<Down>', self.zoom_decrease)
    self.entryNameSize.bind('<Up>',   lambda event: self.font_change("name", +4))
    self.entryNameSize.bind('<Down>', lambda event: self.font_change("name", -4))
    self.entryTypeSize.bind('<Up>',   lambda event: self.font_change("type", +4))
    self.entryTypeSize.bind('<Down>', lambda event: self.font_change("type", -4))
    self.entryNumeroSize.bind('<Up>',   lambda event: self.font_change("numero", +4))
    self.entryNumeroSize.bind('<Down>', lambda event: self.font_change("numero", -4))
    self.entryPowerSize.bind('<Up>',   lambda event: self.font_change("power", +4))
    self.entryPowerSize.bind('<Down>', lambda event: self.font_change("power", -4))
    self.listboxSymbole.bind('<Delete>', self.symbole_del)
    self.listboxSymbole.bind('<Up>',   self.listbox_up)
    self.listboxSymbole.bind('<Down>', self.listbox_down)
    self.listboxSymbole.bind('<Control-Shift-Up>',   lambda event: 'break')
    self.listboxSymbole.bind('<Control-Shift-Down>', lambda event: 'break')
    self.listboxSymbole.bind('<Control-Up>',   lambda event: self.symbole_up(moving=False))
    self.listboxSymbole.bind('<Control-Down>', lambda event: self.symbole_down(moving=False))
    self.bind_all('<Return>', self.update_text)
    
    ########## Conseils ##########
    
    stat_text = 'Ce panneau vous permet de changer les stats %s de la carte. Vous pouvez y entrer un nombre entre 0 et 16. Vous pouvez aussi entrer des demis en tapant par exemple "8,5", "8.5" ou "8 1/2".'
    self.add_tip(self.statCadre, stat_text % "traditionnelles")
    self.add_tip(self.persoCadre, stat_text % "additionnelles" + " Si vous n'y entrez rien, le symbole vert correspondant en arrière-plan ne sera pas affiché. Si vous voulez tout de même afficher le symbole mais vide, entrez \" \".")
    
    champ_text = "Ce champ vous permet d'éditer le %s de la carte."
    self.add_tip(self.entryName, champ_text % "nom")
    self.add_tip(self.entryType, champ_text % "type")
    self.add_tip(self.entryNumero, champ_text % "grand numéro")
    self.add_tip(self.entryPower, champ_text % "petit numéro")
    
    size_text = "Ce champ vous permet de régler la taille de la police d'écriture du %s. Vous devez y entrer un nombre entier. Vous pouvez appuyer sur les touches Haut et Bas pour augmenter ou diminuer de 4 la taille de cette police."
    self.add_tip(self.entryNameSize, size_text % "nom")
    self.add_tip(self.entryTypeSize, size_text % "type")
    self.add_tip(self.entryNumeroSize, size_text % "grand numéro")
    self.add_tip(self.entryPowerSize, size_text % "petit numéro")
    
    default_text = "Appuyez sur ce bouton pour réinitialiser la taille de la police d'écriture du %s, à savoir %d."
    self.add_tip(self.defaultNameButton, default_text % ("nom", DEFAULT_NAME_SIZE))
    self.add_tip(self.defaultTypeButton, default_text % ("type", DEFAULT_TYPE_SIZE))
    self.add_tip(self.defaultNumeroButton, default_text % ("grand numéro", DEFAULT_NUMERO_SIZE))
    self.add_tip(self.defaultPowerButton, default_text % ("petit numéro", DEFAULT_POWER_SIZE))
    
    color_main_text = "Cette liste vous permet de changer la couleur %s. Cette liste de couleur peut être personnalisée en modifiant le fichier \"color.txt\" avec Notepad. Chaque ligne de ce fichier correspond à une couleur. Le format d'une ligne est \"#XXXXXX Nom de la couleur\", où \"#XXXXXX\" est le code de la couleur désirée en hexadécimal."
    color_text = color_main_text % "de la police d'écriture du %s"
    self.add_tip(self.listColorName, color_text % "nom")
    self.add_tip(self.listColorType, color_text % "type")
    self.add_tip(self.listColorNumero, color_text % "grand numéro")
    self.add_tip(self.listColorPower, color_text % "petit numéro")
    self.add_tip(self.listColor, color_main_text % "du fond de la carte")
    self.add_tip(self.listStripColor, color_main_text % "des bandes de la carte")
    
    self.add_tip(self.listSymbole, "Choisissez un symbole dans cette liste, puis cliquez sur le bouton \"＋\" pour l'ajouter à la carte. Une carte ne peut pas avoir plus de 5 symboles.")
    self.add_tip(self.plusButton, "Appuyez sur ce bouton pour ajouter le symbole à côté à la carte. Une carte ne peut pas avoir plus de 5 symboles.")
    self.add_tip(self.supprButton, "Appuyez sur ce bouton pour supprimer le symbole sélectionné (en bleu). Vous pouvez aussi appuyer sur la touche Suppr.")
    self.add_tip(self.allSupprButton, "Appuyez sur ce bouton pour supprimer tous les symboles de la carte.")
    self.add_tip(self.listboxSymbole, "Ceci est la liste des symboles présents sur la carte. Le symbole le plus en haut dans cette liste est celui dessiné le plus en arrière-plan sur la carte, et le symbole le plus en bas est celui le plus en avant-plan sur la carte.")
    self.add_tip(self.symboleCustomButton, 'Appuyez sur ce bouton pour personnalisé le symbole sélectionné (en bleu). Seuls les symboles "Poison" et "Prescience" peuvent être modifiés. Quand vous modifiez un symbole, vous pouvez entrer un nombre qui sera ensuite affiché sur le symbole. Vous pouvez précéder le nombre de la lettre p.')
    self.add_tip(self.symboleDownButton, 'Appuyez sur ce bouton pour descendre le symbole sélectionné (en bleu). Plus un symbole est bas, plus il sera dessiné en avant-plan. Vous pouvez aussi appuyer sur les touches Ctrl et Bas.')
    self.add_tip(self.symboleUpButton, 'Appuyez sur ce bouton pour monter le symbole sélectionné (en bleu). Plus un symbole est haut, plus il sera dessiné en arrière-plan. Vous pouvez aussi appuyer sur les touches Ctrl et Haut.')
    
    self.add_tip(self.listContourColor, "Cette liste vous permet de changer la couleur du contour de l'illustration. Attention, selon le mode que vous avez choisi pour l'illustration, cela peut ne pas être visible.")
    self.add_tip(self.listTemplate, "Cette liste vous permet de changer l'orientation de l'illustration. Cela change également la disposition des autres éléments de la carte.")
    self.add_tip(self.listFaction, "Cette liste vous permet de changer la faction de la carte.")
    self.add_tip(self.listPositionPower, "Cette liste vous permet de changer la position du petit numéro sur la carte.")
    self.add_tip(self.listModeIllus, "Cette liste vous permet de changer le mode d'affichage de l'illustration. Les choix \"Déborde...\" permettent de faire déborder l'illustration. Il y a quatre niveaux de débordement : sous le texte, sous les symboles, sous tout, et par-dessus tout. Le choix \"Contour seul\" affiche le contour mais pas l'illustration. Le choix \"Pas d'illustration\" n'affiche rien.")
    
    self.add_tip(self.canvas, "Cette zone vous permet d'ajuster l'illustration. Faites un clic gauche puis déplacez la souris tout en maintenant le clic gauche pour déplacer l'illustration. Utilisez la molette pour agrandir ou rétrécir l'image. Attention : cette image est une prévisualisation rapide de la vraie carte, il peut y avoir de légères différences quand vous exportez la carte en taille réelle.")
    self.add_tip(self.entryZoom, "Ce champ vous permet de régler le niveau de zoom de l'illustration. Vous pouvez y entrer un nombre décimal avec jusqu'à 2 chiffres après la virgule. Utilisez un point à la place de la virgule. Vous pouvez appuyer sur Haut et Bas pour augmenter ou diminuer le zoom de 1.")
    self.add_tip(self.checkShowIllus, "Cochez cette case pour afficher l'illustration et le cadre polygonal personnalisé autour de l'image. Si vous décochez cette case, il ne restera que le décor plaine et ciel original de l'illustration et le cadre polygonal original.")
    self.add_tip(self.resetButton, "Appuyez sur ce bouton pour réinitialiser la position et le mode de l'illustration, et pour remettre le zoom à sa valeur par défaut.")
    self.add_tip(self.importButton, "Appuyez sur ce bouton pour changer l'illustration en en important une autre depuis votre ordinateur. Les formats supportés sont les images \".jpg\" ou \".jpeg\" et les images \".png\".")
    
    self.add_tip(self.checkFraction, "Cochez cette case pour que le design de la fraction 1/2 soit compacte comme à Magic. Sinon, son design sera large (½).")
    self.add_tip(self.allResetButton, "Appuyez sur ce bouton pour supprimer tous les champs de l'éditeur et pour remettre tous les paramètres à leur valeur par défaut. Ces changements sont irréversibles. Cette opération peut prendre du temps.")
    self.add_tip(self.previewButton, "Appuyez sur ce bouton pour afficher la carte en taille réelle et en qualité optimale. En effet, l'image à gauche de l'éditeur n'est qu'une rapide prévisualisation, il peut y avoir de légères différences entre cette prévisualisation et la carte en taille réelle. Cette opération peut prendre du temps.")
    self.add_tip(self.saveButton, "Appuyez sur ce bouton pour sauvegarder la carte en taille réelle et en qualité optimale. La carte ainsi sauvegardée sera la même que celle que vous voyez en cliquant sur le bouton \"Aperçu (taille réelle)\", et non celle que vous voyez en prévisualisation à gauche de l'éditeur. Cette opération peut prendre du temps.")
    self.add_tip(self.imagePreviewButton, "Appuyez sur ce bouton pour afficher la carte en taille réelle et en qualité optimale, mais avec l'illustration qui déborde intégralement du cadre. Vous pouvez sauvegarder cette image avec le bouton \"Exporter l'image seule\". Ces opérations peuvent prendre du temps.")
    self.add_tip(self.imageSaveButton, "Appuyez sur ce bouton pour sauvegarder la carte en taille réelle et en qualité optimale, mais avec l'illustration qui déborde intégralement du cadre. Ceci est utile si vous voulez effectuer un débordement de l'illustration, car l'illustration se trouve exactement au même endroit sur cette image et sur l'image normale de la carte en taille réelle.")
    self.add_tip(self.entryHelp, "Ce panneau affiche des conseils quand vous survolez une zone de l'éditeur avec votre souris. Décochez la case \"Afficher les conseils\" dans le panneau d'options pour que ce panneau arrête d'afficher des conseils.")
    self.add_tip(self.checkTip, HELP_TEXT)
  
  def tip_write(self, text, bool=True):
    if bool:
      self.entryHelp.config(state=NORMAL)
      self.entryHelp.delete('1.0', END)
      self.entryHelp.insert(END, text)
      self.entryHelp.config(state=DISABLED)
  
  def add_tip(self, widget, text):
    widget.bind('<Enter>', lambda event: self.tip_write(text, bool=self.showTip.get()))
    widget.bind('<Leave>', lambda event: self.tip_write(""))
  
  def cadre_nom(self, editCadre, padx=(0,5), pady=(0,5)):
  
    self.nameCadre = LabelFrame(editCadre, text="Nom", borderwidth=2, relief=GROOVE)
    self.nameCadre.pack(side=TOP, padx=padx, pady=pady)
    
    self.entryName = Entry(self.nameCadre, width=32)
    self.entryName.insert(END, self.carte.name)
    self.entryName.grid(row=0, column=0, sticky=W, columnspan=3, padx=5, pady=5)
    
    Label(self.nameCadre, text="Taille :").grid(row=1, column=0, sticky=E, padx=5)
    self.entryNameSize = Entry(self.nameCadre, width=4)
    self.entryNameSize.insert(END, self.carte.nameSize)
    self.entryNameSize.grid(row=1, column=1, sticky=W, padx=(3,5))
    self.defaultNameButton = Button(self.nameCadre, width=9, text = "Par défaut", command=lambda: self.font_set("name", DEFAULT_NAME_SIZE))
    self.defaultNameButton.grid(row=1, column=2, sticky=W, padx=(0,5), pady=(0,5))
    
    Label(self.nameCadre, text="Couleur :").grid(row=2, column=0, sticky=E, padx=5)
    self.listColorName = OptionMenu(self.nameCadre, self.colorName, *self.availableColor)
    self.listColorName.config(width=15)
    self.listColorName.grid(row=2, column=1, sticky=W, columnspan=2, padx=(0,5), pady=(0,5))
    self.colorName.trace('w', lambda name, index, change: self.update_dict("name"))
  
  def cadre_type(self, editCadre, padx=(0,5), pady=(0,5)):
  
    self.typeCadre = LabelFrame(editCadre, text="Type", borderwidth=2, relief=GROOVE)
    self.typeCadre.pack(side=TOP, padx=padx, pady=pady)
    
    self.entryType = Entry(self.typeCadre, width=32)
    self.entryType.insert(END, self.carte.type)
    self.entryType.grid(row=0, column=0, sticky=W, columnspan=3, padx=5, pady=5)
    
    Label(self.typeCadre, text="Taille :").grid(row=1, column=0, sticky=E, padx=5)
    self.entryTypeSize = Entry(self.typeCadre, width=4)
    self.entryTypeSize.insert(END, self.carte.typeSize)
    self.entryTypeSize.grid(row=1, column=1, sticky=W, padx=(3,5))
    self.defaultTypeButton = Button(self.typeCadre, width=9, text = "Par défaut", command=lambda: self.font_set("type", DEFAULT_TYPE_SIZE))
    self.defaultTypeButton.grid(row=1, column=2, sticky=W, padx=(0,5), pady=(0,5))
    
    Label(self.typeCadre, text="Couleur :").grid(row=2, column=0, sticky=E, padx=5)
    self.listColorType = OptionMenu(self.typeCadre, self.colorType, *self.availableColor)
    self.listColorType.config(width=15)
    self.listColorType.grid(row=2, column=1, sticky=W, columnspan=2, padx=(0,5), pady=(0,5))
    self.colorType.trace('w', lambda name, index, change: self.update_dict("type"))
    
  def cadre_image(self, editCadre, padx=(0,5), pady=(0,5)):
  
    self.illusCadre = LabelFrame(editCadre, text="Illustration", borderwidth=2, relief=GROOVE)
    self.illusCadre.pack(side=TOP, padx=padx, pady=pady)
    
    Label(self.illusCadre, text="Zoom :").grid(row=0, column=0, sticky=E, padx=0)
    self.entryZoom = Entry(self.illusCadre, width=10)
    self.entryZoom.insert(END, zoom_to_string(self.carte.zoom))
    self.entryZoom.grid(row=0, column=1, sticky=W, padx=7)
    
    self.checkShowIllus = Checkbutton(self.illusCadre, text="Afficher l'illustration", variable=self.showIllus)
    # self.checkShowIllus.grid(row=1, column=0, columnspan=2, padx=5, pady=(0,11))
    self.showIllus.trace('w', lambda name, index, change: self.update_dict("illustration"))
    
    Label(self.illusCadre, text="Mode :").grid(row=1, column=0, sticky=E, padx=0)
    self.listModeIllus = OptionMenu(self.illusCadre, self.modeIllus, *self.availableMode)
    self.listModeIllus.config(width=17)
    self.listModeIllus.grid(row=1, column=1, sticky=E, padx=(0,5), pady=(0,1))
    self.modeIllus.trace('w', lambda name, index, change: self.update_dict("mode"))
    
    self.resetButton = Button(self.illusCadre, width=26, text = "Réinitialiser l'illustration", command=self.reset_anchor)
    self.resetButton.grid(row=2, column=0, columnspan=2, padx=7, pady=(1,4))
    self.importButton = Button(self.illusCadre, width=26, text = "Importer une illustration", command=self.open)
    self.importButton.grid(row=3, column=0, columnspan=2, padx=7, pady=(0,5))
    
  def cadre_symbole(self, editCadre, padx=(0,5), pady=(0,5)):
  
    self.symboleCadre = LabelFrame(editCadre, text="Symboles", borderwidth=2, relief=GROOVE)
    self.symboleCadre.pack(side=TOP, padx=padx, pady=pady)
    
    self.symboleSubCadre1 = Frame(self.symboleCadre)
    self.symboleSubCadre1.pack(side=TOP)
    Label(self.symboleSubCadre1, text="Ajouter :").pack(side=LEFT, padx=(3,0))
    # self.listSymbole = OptionMenu(self.symboleSubCadre1, self.addSymbole, *self.availableSymbole)
    
    self.listSymbole = OptionMenu(self.symboleSubCadre1, self.addSymbole, DEFAULT_SYMBOLE)
    self.listSymbole['menu'].delete(0,'end')
    self.listSymboleDict = {}
    symbole_iter = iter(self.availableSymbole)
    for blueprint in self.symboleBlueprint:
      if len(blueprint) == 0:
        self.listSymbole['menu'].insert_separator('end')
      elif len(blueprint) == 1:
        for _ in range(blueprint[0]):
          symbole = next(symbole_iter)
          self.listSymbole['menu'].add_command(label=symbole, command=setit(self.addSymbole, symbole))
      elif len(blueprint) == 2:
        l = []
        name = blueprint[0]
        for _ in range(blueprint[1]):
          l.append(next(symbole_iter))
        self.listSymboleDict[name] = OptionMenu(self.symboleSubCadre1, self.addSymbole, *l)['menu']
        self.listSymbole['menu'].add_cascade(label=name, menu=self.listSymboleDict[name])
    
    self.listSymbole.config(width=12)
    self.listSymbole.pack(side=LEFT, padx=(0,4), pady=(0,5))
    self.plusButton = Button(self.symboleSubCadre1, width=2, text = "＋", command=self.symbole_add)
    self.plusButton.pack(side=LEFT, padx=(0,7), pady=(0,5))
    
    self.listboxSymbole = Listbox(self.symboleCadre, name="listbox_symbole", activestyle=NONE, height=MAX_SYMBOLE, width=30)
    self.listboxSymbole.pack(side=TOP, pady=(0,7))
    
    self.symboleSubCadre2 = Frame(self.symboleCadre)
    self.symboleSubCadre2.pack(side=TOP)
    self.supprButton = Button(self.symboleSubCadre2, text = "Supprimer", command=self.symbole_del)
    self.supprButton.pack(side=LEFT, padx=(5,5), pady=(0,7))
    self.allSupprButton = Button(self.symboleSubCadre2, text = "Tout supprimer", command=self.symbole_del_all)
    self.allSupprButton.pack(side=LEFT, padx=(0,5), pady=(0,7))
    
    self.symboleSubCadre3 = Frame(self.symboleCadre)
    self.symboleSubCadre3.pack(side=TOP)
    self.symboleCustomButton = Button(self.symboleSubCadre3, text="Modifier", state=DISABLED, command=self.symbole_custom)
    self.symboleCustomButton.pack(side=LEFT, padx=5, pady=(0,5))
    Label(self.symboleSubCadre3, text="Déplacer :").pack(side=LEFT, padx=(0,5))
    self.symboleDownButton = Button(self.symboleSubCadre3, width=2, text = "˅", command=self.symbole_down)
    self.symboleDownButton.pack(side=LEFT, padx=(0,5), pady=(0,5))
    self.symboleUpButton = Button(self.symboleSubCadre3, width=2, text = "˄", command=self.symbole_up)
    self.symboleUpButton.pack(side=LEFT, padx=(0,5), pady=(0,5))
  
  def cadre_numero(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.numeroCadre = LabelFrame(editCadre, text="Défense", borderwidth=2, relief=GROOVE)
    self.numeroCadre.pack(side=TOP, padx=padx, pady=pady)
    
    self.numeroCadreTop = Frame(self.numeroCadre)
    self.numeroCadreTop.pack(side=TOP)
    Label(self.numeroCadreTop, text="Gros numéro :").grid(row=0, column=0, sticky=E, padx=(42,5), pady=4)
    self.entryNumero = Entry(self.numeroCadreTop, width=5)
    self.entryNumero.grid(row=0, column=1, sticky=E, padx=(0,44), pady=(3,2))
    
    self.numeroCadreBot = Frame(self.numeroCadre)
    self.numeroCadreBot.pack(side=TOP)
    Label(self.numeroCadreBot, text="Taille :").grid(row=1, column=0, sticky=E, padx=5)
    self.entryNumeroSize = Entry(self.numeroCadreBot, width=4)
    self.entryNumeroSize.insert(END, self.carte.numeroSize)
    self.entryNumeroSize.grid(row=1, column=1, sticky=W, padx=(3,5))
    self.defaultNumeroButton = Button(self.numeroCadreBot, width=9, text = "Par défaut", command=lambda: self.font_set("numero", DEFAULT_NUMERO_SIZE))
    self.defaultNumeroButton.grid(row=1, column=2, sticky=W, padx=(0,5), pady=(0,5))
    
    Label(self.numeroCadreBot, text="Couleur :").grid(row=2, column=0, sticky=E, padx=5)
    self.listColorNumero = OptionMenu(self.numeroCadreBot, self.colorNumero, *self.availableColor)
    self.listColorNumero.config(width=15)
    self.listColorNumero.grid(row=2, column=1, sticky=W, columnspan=2, padx=(0,5), pady=(0,5))
    self.colorNumero.trace('w', lambda name, index, change: self.update_dict("numero"))
  
  def cadre_power(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.powerCadre = LabelFrame(editCadre, text="Pouvoir", borderwidth=2, relief=GROOVE)
    self.powerCadre.pack(side=TOP, padx=padx, pady=pady)
    
    self.powerCadreTop = Frame(self.powerCadre)
    self.powerCadreTop.pack(side=TOP)
    Label(self.powerCadreTop, text="Petit numéro :").grid(row=0, column=0, sticky=E, padx=(42,5), pady=(4+10,4))
    self.entryPower = Entry(self.powerCadreTop, width=5)
    self.entryPower.grid(row=0, column=1, sticky=E, padx=(0,44), pady=(3+10,2))
    
    self.powerCadreBot = Frame(self.powerCadre)
    self.powerCadreBot.pack(side=TOP)
    Label(self.powerCadreBot, text="Taille :").grid(row=1, column=0, sticky=E, padx=5)
    self.entryPowerSize = Entry(self.powerCadreBot, width=4)
    self.entryPowerSize.insert(END, self.carte.powerSize)
    self.entryPowerSize.grid(row=1, column=1, sticky=W, padx=(3,5))
    self.defaultPowerButton = Button(self.powerCadreBot, width=9, text = "Par défaut", command=lambda: self.font_set("power", DEFAULT_POWER_SIZE))
    self.defaultPowerButton.grid(row=1, column=2, sticky=W, padx=(0,5), pady=(0,5))
    
    Label(self.powerCadreBot, text="Couleur :").grid(row=2, column=0, sticky=E, padx=5)
    self.listColorPower = OptionMenu(self.powerCadreBot, self.colorPower, *self.availableColor)
    self.listColorPower.config(width=15)
    self.listColorPower.grid(row=2, column=1, sticky=W, columnspan=2, padx=(0,5), pady=0)
    self.colorPower.trace('w', lambda name, index, change: self.update_dict("power"))
    
    Label(self.powerCadreBot, text="Position :").grid(row=3, column=0, sticky=E, padx=5, pady=(0,23))
    self.listPositionPower = OptionMenu(self.powerCadreBot, self.positionPower, *self.availablePosition)
    self.listPositionPower.config(width=15)
    self.listPositionPower.grid(row=3, column=1, sticky=W, columnspan=2, padx=(0,5), pady=(0,5+23))
    self.positionPower.trace('w', lambda name, index, change: self.update_dict("position"))
  
  def cadre_stat(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.statCadre = LabelFrame(editCadre, text="Stats", borderwidth=2, relief=GROOVE)
    self.statCadre.pack(side=TOP, padx=padx, pady=pady)
    self.entryStat = {}
    
    i=0
    for stat in ALL_STAT:
      Label(self.statCadre, text=stat_to_string(stat)+":").grid(row=i, column=0, sticky=E, padx=(43,5), pady=(2 if i==0 else 0,7 if i==5 else 5))
      self.entryStat[stat] = Entry(self.statCadre, width=5)
      self.entryStat[stat].insert(END, self.carte.stats[stat])
      self.entryStat[stat].grid(row=i, column=1, sticky=E, padx=(0,44), pady=(2 if i==0 else 0,7 if i==5 else 5))
      i+=1
    
  def cadre_perso(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.persoCadre = LabelFrame(editCadre, text="Personnalité", borderwidth=2, relief=GROOVE)
    self.persoCadre.pack(side=TOP, padx=padx, pady=pady)
    
    Label(self.persoCadre, text="Chance :").grid(row=0, column=1, sticky=E, padx=(61,5), pady=(0,5))
    self.entryLuck = Entry(self.persoCadre, width=5)
    self.entryLuck.insert(END, self.carte.chance)
    self.entryLuck.grid(row=0, column=2, sticky=E, padx=(0,44), pady=(0,5))
    
    Label(self.persoCadre, text="Charisme :").grid(row=1, column=1, sticky=E, padx=(61,5), pady=(0,5))
    self.entryCharisma = Entry(self.persoCadre, width=5)
    self.entryCharisma.insert(END, self.carte.charisme)
    self.entryCharisma.grid(row=1, column=2, sticky=E, padx=(0,44), pady=(0,5))
    
  def cadre_template(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.templateCadre = LabelFrame(editCadre, text="Template", borderwidth=2, relief=GROOVE)
    self.templateCadre.pack(side=TOP, padx=padx, pady=pady)
    
    Label(self.templateCadre, text="Fond :").grid(row=0, column=0, sticky=E, padx=(5,5))
    self.listColor = OptionMenu(self.templateCadre, self.color, *self.availableColor)
    self.listColor.config(width=15)
    self.listColor.grid(row=0, column=1, columnspan=2, sticky=W, padx=(0,5))
    self.color.trace('w', lambda name, index, change: self.update_dict("fond"))
    
    Label(self.templateCadre, text="Bandes :").grid(row=1, column=0, sticky=E, padx=(8,5))
    self.listStripColor = OptionMenu(self.templateCadre, self.colorStrip, *self.availableColor)
    self.listStripColor.config(width=15)
    self.listStripColor.grid(row=1, column=1, columnspan=2, sticky=W, padx=(0,8))
    self.colorStrip.trace('w', lambda name, index, change: self.update_dict("bande"))
    
    Label(self.templateCadre, text="Contour :").grid(row=2, column=0, columnspan=2, sticky=E, padx=(20,5))
    self.listContourColor = OptionMenu(self.templateCadre, self.contourColor, "Noir", "Gris")
    self.listContourColor.config(width=12)
    self.listContourColor.grid(row=2, column=2, sticky=W, padx=(0,8))
    self.contourColor.trace('w', lambda name, index, change: self.update_dict("contour"))
    
    Label(self.templateCadre, text="Illustration :").grid(row=3, column=0, columnspan=2, sticky=E, padx=(5,5))
    self.listTemplate = OptionMenu(self.templateCadre, self.template, *self.availableTemplate)
    self.listTemplate.config(width=12)
    self.listTemplate.grid(row=3, column=2, sticky=W, padx=(0,5))
    self.template.trace('w', lambda name, index, change: self.update_dict("template"))
    
    Label(self.templateCadre, text="Faction :").grid(row=4, column=0, columnspan=2, sticky=E, padx=(5,5))
    self.listFaction = OptionMenu(self.templateCadre, self.faction, *self.availableFaction)
    self.listFaction.config(width=12)
    self.listFaction.grid(row=4, column=2, sticky=W, padx=(0,5), pady=(0,5))
    self.faction.trace('w', lambda name, index, change: self.update_dict("faction"))
  
  def cadre_save(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.saveCadre = LabelFrame(editCadre, text="Carte", borderwidth=2, relief=GROOVE)
    self.saveCadre.pack(side=TOP, padx=padx, pady=pady)

    self.allResetButton = Button(self.saveCadre, width=22, text = "✕   Tout supprimer   ✕", command=self.reset)
    self.allResetButton.grid(row=0, column=0, columnspan=2, padx=7, pady=(10,19))
    self.imagePreviewButton = Button(self.saveCadre, width=26, text = "Aperçu de l'illustration seule", command=self.previewFullIllus)
    # self.imagePreviewButton.grid(row=1, column=0, columnspan=2, padx=7, pady=(0,4))
    self.imageSaveButton = Button(self.saveCadre, width=26, text = "Exporter l'illustration seule", command=self.saveFullIllus)
    # self.imageSaveButton.grid(row=2, column=0, columnspan=2, padx=7, pady=(0,5))
    self.previewButton = Button(self.saveCadre, width=26, text = "Aperçu (taille réelle)", command=self.preview)
    self.previewButton.grid(row=3, column=0, columnspan=2, padx=7, pady=(0,4))
    self.saveButton = Button(self.saveCadre, width=26, text = "Exporter (taille réelle)", command=self.save) #default=ACTIVE, font=('segoe ui', 9, 'italic')
    self.saveButton.grid(row=4, column=0, columnspan=2, padx=7, pady=(0,4))
  
  def cadre_option(self, editCadre, padx=(0,5), pady=(0,5)):
    
    self.optionCadre = LabelFrame(editCadre, text="Options", borderwidth=2, relief=GROOVE)
    self.optionCadre.pack(side=TOP, padx=padx, pady=pady)
    
    self.checkFraction = Checkbutton(self.optionCadre, text="Fractions compactes", variable=self.chooseFraction, bd=0)
    self.checkFraction.pack(padx=(20,53), pady=(4,1))
    self.chooseFraction.trace('w', lambda name, index, change: self.update_dict("fraction"))
    
    # self.checkOutline = Checkbutton(self.optionCadre, text="Contours du nom", variable=self.showOutline)
    # self.checkOutline.pack(padx=(20,64), pady=(0,7))
    # self.showOutline.trace('w', lambda name, index, change: self.update_dict("outline"))
    
    self.checkTip = Checkbutton(self.optionCadre, text="Afficher les conseils", variable=self.showTip, bd=0)
    self.checkTip.pack(padx=(20,57), pady=(0,5))
    self.showTip.trace('w', lambda name, index, change: self.tip_write(HELP_TEXT if self.showTip.get() else ""))
    
    # Button(self.optionCadre, width=26, text = "Aide et astuces", command=self.help).pack(padx=7, pady=(0,8))
  
  def update_picture(self, updatePhoto = False):
    if not self.lazy:
      if updatePhoto:
        self.carte.update_photo()
      self.photo = ImageTk.PhotoImage(self.carte.picturize())
      self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
  
  def init_update_anchor(self, event):
    self.anchorLast = (event.x, event.y)
  
  def anchor_move(self, event):
    x, y = self.carte.anchor
    incr_x, incr_y = self.anchorLast
    incr_x = round(incr_x - event.x) #* self.carte.cardDisplayRatio
    incr_y = round(incr_y - event.y) #* self.carte.cardDisplayRatio
    self.carte.anchor = (x - incr_x, y - incr_y)
    self.anchorLast = (event.x, event.y)
    self.update_picture()
    
  def anchor_zoom(self, event):
    self.carte.centeringZoom(
      event.x, #* self.carte.cardDisplayRatio
      event.y, #* self.carte.cardDisplayRatio
      pow(1.1,event.delta / self.mouseWheelTick)
    )
    self.entryZoom.delete(0, 'end')
    self.entryZoom.insert(END, zoom_to_string(self.carte.zoom))
    self.update_picture()
    
  def update_zoom(self, new_zoom):
    old_zoom = self.carte.zoom
    self.carte.centeringZoom(
      (self.carte.illusX + self.carte.contour_w // 2) // self.carte.cardDisplayRatio,
      (self.carte.illusY + self.carte.contour_h // 2) // self.carte.cardDisplayRatio,
      new_zoom/old_zoom
    )
    self.entryZoom.delete(0, 'end')
    self.entryZoom.insert(END, zoom_to_string(self.carte.zoom))
  
  def zoom_increase(self, event = None):
    new_zoom = self.carte.zoom + .01
    self.update_zoom(new_zoom)
    self.update_picture()
  
  def zoom_decrease(self, event = None):
    new_zoom = self.carte.zoom - .01
    if new_zoom >= .001:
      self.update_zoom(new_zoom)
      self.update_picture()
  
  def font_change(self, line, increase):
    if line == "name":
      self.carte.nameSize += increase
      if self.carte.nameSize <= 0:
        self.carte.nameSize -= increase
      self.entryNameSize.delete(0, 'end')
      self.entryNameSize.insert(END, str(self.carte.nameSize))
    elif line == "type":
      self.carte.typeSize += increase
      if self.carte.typeSize <= 0:
        self.carte.typeSize -= increase
      self.entryTypeSize.delete(0, 'end')
      self.entryTypeSize.insert(END, str(self.carte.typeSize))
    elif line == "numero":
      self.carte.numeroSize += increase
      if self.carte.numeroSize <= 0:
        self.carte.numeroSize -= increase
      self.entryNumeroSize.delete(0, 'end')
      self.entryNumeroSize.insert(END, str(self.carte.numeroSize))
    elif line == "power":
      self.carte.powerSize += increase
      if self.carte.powerSize <= 0:
        self.carte.powerSize -= increase
      self.entryPowerSize.delete(0, 'end')
      self.entryPowerSize.insert(END, str(self.carte.powerSize))
    self.update_picture()
    
  def font_set(self, line, value):
    if line == "name":
      self.carte.nameSize = value
      self.entryNameSize.delete(0, 'end')
      self.entryNameSize.insert(END, str(self.carte.nameSize))
    elif line == "type":
      self.carte.typeSize = value
      self.entryTypeSize.delete(0, 'end')
      self.entryTypeSize.insert(END, str(self.carte.typeSize))
    elif line == "numero":
      self.carte.numeroSize = value
      self.entryNumeroSize.delete(0, 'end')
      self.entryNumeroSize.insert(END, str(self.carte.numeroSize))
    elif line == "power":
      self.carte.powerSize = value
      self.entryPowerSize.delete(0, 'end')
      self.entryPowerSize.insert(END, str(self.carte.powerSize))
    self.update_picture()
  
  def symbole_update_button(self):
    if self.listboxSymbole.size() > 0:
      self.symboleCustomButton.config(state=NORMAL)
    else:
      self.symboleCustomButton.config(state=DISABLED)
  
  def symbole_custom(self, event=None):
    name = symbole_name(self.listboxSymbole.get(ACTIVE))
    if "custom" not in self.carte.symbole_dict[name]:
      showinfo("La modification a échoué", "Le symbole %s ne peut pas être personnalisé." % self.listboxSymbole.get(ACTIVE))
    else:
      result = CustomDialog(self, self.listboxSymbole.get(ACTIVE)).result
      if result == None:
        pass
      elif result == '':
        self.symbole_rename(name)
      else:
        self.symbole_rename('%s (%s)' % (name, result))
    
  def symbole_add(self):
    if self.listboxSymbole.size() < MAX_SYMBOLE:
      self.listboxSymbole.insert(END, self.addSymbole.get())
      self.listboxSymbole.selection_set(ACTIVE)
    self.symbole_update_button()
    self.update_text()
  
  def symbole_add_here(self):
    if self.listboxSymbole.size() < MAX_SYMBOLE:
      self.listboxSymbole.insert(ACTIVE, self.addSymbole.get())
      self.listboxSymbole.selection_set(ACTIVE)
    self.symbole_update_button()
    self.update_text()
  
  def symbole_rename(self, name):
    position = self.listboxSymbole.index(ACTIVE)
    self.listboxSymbole.insert(ACTIVE, name)
    self.listboxSymbole.delete(ACTIVE)
    self.listboxSymbole.selection_clear(0, END)
    self.listboxSymbole.selection_set(position)
    self.listboxSymbole.selection_anchor(position)
    self.listboxSymbole.activate(position)
    self.update_text()
  
  def symbole_del(self, event=None):
    self.listboxSymbole.delete(ACTIVE)
    self.listboxSymbole.selection_set(ACTIVE)
    self.symbole_update_button()
    self.update_text()
  
  def symbole_del_all(self, event=None):
    self.listboxSymbole.delete(0, END)
    self.symbole_update_button()
    self.update_text()
  
  def listbox_up(self, event=None):
    if self.listboxSymbole.index(ACTIVE) > 0:
      position = self.listboxSymbole.index(ACTIVE)
      self.listboxSymbole.selection_clear(0, END)
      self.listboxSymbole.selection_set(position-1)
      self.listboxSymbole.selection_anchor(position-1)
      self.listboxSymbole.activate(position-1)
    # self.symbole_update_button()
    return 'break'
  
  def listbox_down(self, event=None):
    if self.listboxSymbole.index(ACTIVE) < self.listboxSymbole.size()-1:
      position = self.listboxSymbole.index(ACTIVE)
      self.listboxSymbole.selection_clear(0, END)
      self.listboxSymbole.selection_set(position+1)
      self.listboxSymbole.selection_anchor(position+1)
      self.listboxSymbole.activate(position+1)
    # self.symbole_update_button()
    return 'break'
  
  def symbole_up(self, event=None, moving=True):
    if self.listboxSymbole.index(ACTIVE) > 0:
      symbole  = self.listboxSymbole.get(ACTIVE)
      position = self.listboxSymbole.index(ACTIVE)
      new_position = position-1 if moving else position
      self.listboxSymbole.delete(position)
      self.listboxSymbole.insert(position-1, symbole)
      self.listboxSymbole.selection_clear(0, END)
      self.listboxSymbole.selection_set(new_position)
      self.listboxSymbole.selection_anchor(new_position)
      self.listboxSymbole.activate(new_position)
    # self.symbole_update_button()
    self.update_text()
  
  def symbole_down(self, event=None, moving=True):
    if self.listboxSymbole.index(ACTIVE) < self.listboxSymbole.size()-1:
      symbole  = self.listboxSymbole.get(ACTIVE)
      position = self.listboxSymbole.index(ACTIVE)
      new_position = position+1 if moving else position
      self.listboxSymbole.delete(position)
      self.listboxSymbole.insert(position+1, symbole)
      self.listboxSymbole.selection_clear(0, END)
      self.listboxSymbole.selection_set(new_position)
      self.listboxSymbole.selection_anchor(new_position)
      self.listboxSymbole.activate(new_position)
    # self.symbole_update_button()
    self.update_text()
  
  def update_text(self, event = None):
    self.carte.name = self.entryName.get()
    self.carte.type = self.entryType.get()
    self.carte.symboleList = self.listboxSymbole.get(0, END)
    self.carte.numero = self.entryNumero.get()
    self.carte.power = self.entryPower.get()
    self.font_set("name", self.numberProj(self.entryNameSize.get(), default = self.carte.nameSize))
    self.font_set("type", self.numberProj(self.entryTypeSize.get(), default = self.carte.typeSize))
    self.font_set("numero", self.numberProj(self.entryNumeroSize.get(), default = self.carte.numeroSize))
    self.font_set("power", self.numberProj(self.entryPowerSize.get(), default = self.carte.powerSize))
    new_zoom = self.carte.getNewZoom(self.entryZoom.get())
    self.update_zoom(new_zoom)
    self.carte.chance   = self.entryLuck.get()
    self.carte.charisme = self.entryCharisma.get()
    for stat in ALL_STAT:
      self.carte.stats[stat] = self.entryStat[stat].get()
    self.update_picture()
    
  def update_dict(self, field):
    if field == "name": self.carte.nameColor = self.carte.color_dict[self.colorName.get()]
    if field == "type": self.carte.typeColor = self.carte.color_dict[self.colorType.get()]
    if field == "numero": self.carte.numeroColor = self.carte.color_dict[self.colorNumero.get()]
    if field == "power": self.carte.powerColor = self.carte.color_dict[self.colorPower.get()]
    if field == "position": self.carte.powerPosition = self.carte.position_dict[self.positionPower.get()]
    if field == "mode": self.carte.illusMode = self.carte.mode_dict[self.modeIllus.get()]
    if field == "fond": self.carte.color = self.carte.color_dict[self.color.get()]
    if field == "contour": self.carte.contourColor = self.contourColor.get()
    if field == "bande": self.carte.stripColor = self.carte.color_dict[self.colorStrip.get()]
    if field == "faction": self.carte.faction = self.carte.faction_dict[self.faction.get()]
    if field == "template": self.carte.template = self.template.get()
    if field == "illustration": self.carte.showIllus = self.showIllus.get()
    if field == "outline": self.carte.showOutline = self.showOutline.get()
    if field == "fraction": self.carte.chooseFraction = self.chooseFraction.get()
    self.update_picture(updatePhoto = (field == "template"))
  
  def reset_anchor(self):
    self.carte.anchor = self.carte.defaultAnchor
    self.carte.zoom = 1.0
    self.entryZoom.delete(0, 'end')
    self.entryZoom.insert(END, zoom_to_string(self.carte.zoom))
    self.carte.showIllus = True
    self.modeIllus.set(DEFAULT_MODE)
    self.showIllus.set(1)
    self.update_picture()
  
  def set_entry(self, entry, text):
    entry.delete(0, 'end')
    entry.insert('end', text)
  
  def reset(self):
    if ResetDialog(self, "Tout supprimer").result:
      self.lazy = True
      self.set_entry(self.entryName, "")
      self.set_entry(self.entryNameSize, DEFAULT_NAME_SIZE)
      self.colorName.set(DEFAULT)
      self.set_entry(self.entryType, "")
      self.set_entry(self.entryTypeSize, DEFAULT_TYPE_SIZE)
      self.colorType.set(DEFAULT)
      self.set_entry(self.entryNumero, "")
      self.set_entry(self.entryNumeroSize, DEFAULT_NUMERO_SIZE)
      self.colorNumero.set(DEFAULT)
      self.set_entry(self.entryPower, "")
      self.set_entry(self.entryPowerSize, DEFAULT_POWER_SIZE)
      self.colorPower.set(DEFAULT)
      self.positionPower.set(DEFAULT_POWER_POSITION)
      self.addSymbole.set(DEFAULT_SYMBOLE)
      for stat in ALL_STAT:
        self.set_entry(self.entryStat[stat], "")
      self.set_entry(self.entryLuck, "")
      self.set_entry(self.entryCharisma, "")
      self.color.set(DEFAULT_COLOR)
      self.colorStrip.set(DEFAULT_STRIP_COLOR)
      self.contourColor.set(DEFAULT_CONTOUR_COLOR)
      self.faction.set(DEFAULT_SYMBOLE)
      self.chooseFraction.set(1)
      self.reset_anchor()
      self.symbole_del_all()
      self.update_text()
      self.lazy = False
      if self.template.get() != DEFAULT_TEMPLATE:
        self.template.set(DEFAULT_TEMPLATE)
      else:
        self.update_picture(updatePhoto = True)
  
  def open(self, event = None):
    name = filedialog.askopenfilename(filetypes=[('Fichiers supportés', '.png .jpg .jpeg')])
    if name:
      self.carte.illustration.close()
      self.carte.illustration = Image.open(name)
      if self.carte.illustration.mode == "RGB":
        a_channel = Image.new('L', self.carte.illustration.size, 255)
        self.carte.illustration.putalpha(a_channel)
      self.reset_anchor()
      self.update_picture()
  
  def help(self, event = None):
    showinfo("Aide et astuces", "Ce menu est en cours de rédaction, veuillez attendre la prochaine mise à jour.")
  
  def save(self, event = None):
    name = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[('Fichiers images', '.png'), ('Tous les fichiers', '.*')], initialfile=self.carte.name)
    if name:
      self.carte.picturize(display = False).save(name, "PNG")
  
  def saveFullIllus(self, event = None):
    name = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[('Fichiers images', '.png'), ('Tous les fichiers', '.*')], initialfile=self.carte.name + " - image seule")
    if name:
      self.carte.picturize(display = False, illusOnly = True).save(name, "PNG")
    
  def preview(self, event = None):
    self.carte.picturize(display = False).show() 
    
  def previewFullIllus(self, event = None):
    self.carte.picturize(display = False, illusOnly = True).show()
  
  def numberProj(self, number, default=""):
    try:
      ans = int(number)
      assert ans > 0
      return ans
    except:
      return default
    
def main():
  fenetre = Tk()
  fenetre.withdraw() # hide the window
  fenetre.after(0,fenetre.deiconify) # show it again when done
  fenetre.resizable(False, False)
  fenetre.title("Baston Editor")
  fenetre.iconbitmap("src/pic/shield.ico")
  interface = Interface(fenetre)
  interface.mainloop()

if __name__ == "__main__":
  main()