{"main":
 {"style": "background-image:url($path/tnbg2.png);",
  "size": [300, 620],
  "icon": "$path/trayicon3.gif",
  "close": { "image": "$path/x.gif",
             "loc": [255, 0]},
  "minimize": { "image": "$path/m.gif",
                "loc": [225, 0]},
  "menubar": { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px; background-color: #e5000f; border:2px solid #ff0000",
             "selected": "background-color: #ff0000"
           },
  "chums": { "style": "background-color: white;color: black;font: bold;font-family: 'Courier New';selection-background-color:#ffb6b6; ",
             "loc": [20, 65],
             "size": [265, 450],
             "moods": { "chummy": { "icon": "$path/chummy.gif",
                                    "color": "black" },
                        "offline": { "icon": "$path/offline.gif",
                                     "color": "#dbdbdb"},
                        "rancorous": { "icon": "$path/rancorous.gif",
                                       "color": "red" }
                      }
           },
  "defaultwindow": { "style": "background: #e5000f; font-family:'Courier New';font:bold;selection-background-color:#ffb6b6; " 
                   },
  "labels": { "mychumhandle": "MYTROLLTAG" },
  "elements": [
      { "style": "" }
  ]
 },
 "convo":
 {"style": "background: #e5000f; font-family: 'Courier New'",
  "size": [600, 500],
  "chumlabel": { "style": "background: rgba(255, 255, 255, 25%);" },
  "textarea": {
      "style": "background: white;"
  },
  "input": {
      "style": "background: white;"
  },
  "tabstyle": 0
 }
 
}
