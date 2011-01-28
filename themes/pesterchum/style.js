{"main":
 {"style": "background-image:url($path/pcbg.png);",
  "size": [300, 620],
  "icon": "$path/trayicon.gif",
  "close": { "image": "$path/x.gif",
             "loc": [275, 0]},
  "minimize": { "image": "$path/m.gif",
                "loc": [255, 0]},
  "menubar": { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px; background-color: #fdb302;border:2px solid #ffff00",
             "selected": "background-color: #ffff00"
           },
  "chums": { "style": "background-color: black;color: white;font: bold;font-family: 'Courier New';selection-background-color:#919191; ",
             "loc": [20, 65],
             "size": [265, 400],
             "moods": { "chummy": { "icon": "$path/chummy.gif",
                                    "color": "white" },
                        "offline": { "icon": "$path/offline.gif",
                                     "color": "#919191"},
                        "rancorous": { "icon": "$path/rancorous.gif",
                                       "color": "red" }
                      }
           },
  "defaultwindow": { "style": "background: #fdb302; font-family:'Courier New';font:bold;" 
                   },
  "labels": { "mychumhandle": "MYCHUMHANDLE" },
  "elements": [
      { "style": "" }
  ]
 },
 "convo":
 {"style": "background: #fdb302; font-family: 'Courier New'",
  "size": [500, 500],
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
