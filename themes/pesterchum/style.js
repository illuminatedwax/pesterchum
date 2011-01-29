{"main":
 {"style": "background-image:url($path/pcbg.png);",
  "size": [300, 620],
  "icon": "$path/trayicon.gif",
  "newmsgicon": "$path/trayicon2.png",
  "close": { "image": "$path/x.gif",
             "loc": [275, 0]},
  "minimize": { "image": "$path/m.gif",
                "loc": [255, 0]},
  "menubar": { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier New'; font-weight: bold; font-size: 12px; background-color: #fdb302;border:2px solid #ffff00",
             "selected": "background-color: #ffff00"
           },
  "sounds": { "alertsound": "$path/alarm.wav" },
  "chums": { "style": "background-color: black;color: white;font: bold;font-family: 'Courier New';selection-background-color:#919191; ",
             "loc": [20, 65],
             "size": [266, 270],
             "moods": { "chummy": { "icon": "$path/chummy.gif",
                                    "color": "white" },
                        "offline": { "icon": "$path/offline.gif",
                                     "color": "#919191"},
                        "rancorous": { "icon": "$path/rancorous.gif",
                                       "color": "red" },
						"detestful": { "icon": "$path/detestful.gif",
									   "color": "red" },
						"devious": { "icon": "$path/devious.gif",
									 "color": "white" },
						"discontent": { "icon": "$path/discontent.gif",
										"color": "white" },
						"distraught": { "icon": "$path/distraught.gif",
										"color": "white" },
						"ecstatic": { "icon": "$path/estatic.gif",
									  "color": "white" },
						"pleasant": { "icon": "$path/pleasant.gif",
									  "color": "white" },
						"relaxed": { "icon": "$path/relaxed.gif",
									 "color": "white" },
						"sleek": { "icon": "$path/sleek.gif",
								   "color": "white" },
						"smooth": { "icon": "$path/smooth.gif",
									"color": "white" },
						"unruly": { "icon": "$path/unruly.gif",
									"color": "white" }
                      }
           },
  "mychumhandle": { "label": { "text": "MYCHUMHANDLE",
                               "loc": [70,410],
                               "style": "color:black;font:bold;" },
                    "handle": { "style": "border:3px solid yellow; background: black; color:white;",
                                "loc": [20,430],
                                "size": [220,30] },
                    "colorswatch": { "loc": [243,430],
                                     "size": [40,30],
                                     "text": "" }
                  },
  "defaultwindow": { "style": "background: #fdb302; font-family:'Courier New';font:bold;selection-background-color:#919191; " 
                   },
  "addchum": { "style": "background: #fdb302; border:5px solid yellow; font: bold;",
               "loc": [20,340],
               "size": [100, 40],
               "text": "ADD CHUM"
             },
  "pester": { "style": "background: #fdb302; border:5px solid yellow; font: bold;",
               "loc": [130,340],
               "size": [100, 40],
               "text": "PESTER!"
             },
  "defaultmood": 0,
  "moods": [
      { "style": "text-align:left; background: white; border:3px solid black; padding: 5px;color:#919191;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 470],
		"size": [133, 30],
	    "text": "CHUMMY",
		"icon": "$path/chummy.gif",
		"mood": 0
	  },
	  { "style": "text-align:left; background: white; border:3px solid black; padding: 5px;color: #919191", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 497],
		"size": [133, 30],
		"text": "PLEASANT",
		"icon": "$path/pleasant.gif",
		"mood": 3
	  },
	  { "style": "text-align:left; background: white; border:3px solid black; padding: 5px;color:#919191;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 524],
		"size": [133, 30],
		"text": "DISTRAUGHT",
		"icon": "$path/distraught.gif",
		"mood": 4
	  },
	  { "style": "text-align:left; background: white; border:3px solid black; padding: 5px;color:#919191;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [150, 470],
		"size": [133, 30],
		"text": "UNRULY",
		"icon": "$path/unruly.gif",
		"mood": 5
	  },
	  { "style": "text-align:left; background: white; border:3px solid black; padding: 5px;color:#919191;", 
		"selected": "text-align:left; background: white; border:3px solid black; padding: 5px;font: bold;",
		"loc": [150, 497],
		"size": [133, 30],
		"text": "SMOOTH",
		"icon": "$path/smooth.gif",
		"mood": 6
	  },
	  { "style": "text-align:left; background: red; border:3px solid black; padding: 5px;", 
		"selected": "text-align:left; background: red; border:3px solid black; padding: 5px;font: bold;",
		"loc": [150, 524],
		"size": [133, 30],
		"text": "RANCOROUS",
		"icon": "$path/rancorous.gif",
		"mood": 1
	  },
	  { "style": "text-align:center; background: #919191; border:3px solid black; padding: 5px;", 
		"selected": "text-align:center; background: #919191; border:3px solid black; padding: 5px;font: bold;",
		"loc": [20, 551],
		"size": [263, 30],
		"text": "ABSCOND",
		"icon": "$path/offline.gif",
		"mood": 2
	  }
  ]
 },
 "convo":
 {"style": "background: #fdb302; font-family: 'Courier New'",
  "size": [600, 500],
  "chumlabel": { "style": "background: rgba(255, 255, 255, 25%);" },
  "textarea": {
      "style": "background: white;"
  },
  "input": {
      "style": "background: white;"
  },
  "tabs": {
      "style": "",
      "newmsgcolor": "#fdb302",
      "tabstyle": 0
  }
 }
 
}
