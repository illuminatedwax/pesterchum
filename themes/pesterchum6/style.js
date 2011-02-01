{"main":
 {"style": "background-image:url($path/pcbg.png);",
  "size": [232, 380],
  "icon": "$path/trayicon.gif",
  "newmsgicon": "$path/trayicon2.gif",
  "windowtitle": "PESTERCHUM",
  "close": { "image": "$path/x.gif",
             "loc": [210, 2]},
  "minimize": { "image": "$path/m.gif",
                "loc": [190, 2]},
  "menubar": { "style": "font-family: 'Courier'; font:bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier'; font: bold; font-size: 12px; background-color: #fdb302;border:2px solid #ffff00",
             "selected": "background-color: #ffff00"
           },
  "sounds": { "alertsound": "$path/alarm.wav" },
  "chums": { "style": "border:2px solid yellow; background-color: black;color: white;font: bold;font-family: 'Courier';selection-background-color:#646464; ",
             "loc": [12, 117],
             "size": [209, 82],
             "moods": { "chummy": { "icon": "$path/chummy.gif",
                                    "color": "white" },
                        "offline": { "icon": "$path/offline.gif",
                                     "color": "#646464"},
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
  "mychumhandle": { "label": { "text": "CHUMHANDLE:",
                               "loc": [19,232],
                 "style": "color: rgba(255, 255, 0, 0%) ; font-family: 'Courier';" },
                    "handle": { "style": "background: black; padding: 3px; color:white; font-family:'Courier';  font:bold; text-align:left;",
                             "loc": [14,246],
                                "size": [190, 21] },
                    "colorswatch": { "loc": [196,246],
                                     "size": [23,21],
                                     "text": "" }
                  },
  "defaultwindow": { "style": "background: #fdb302; font-family:'Courier';font:bold;selection-background-color:#919191; " 
                   },
  "addchum":  { "style": "background: rgba(255, 255, 0, 0%); border:2px solid #c48a00; font: bold; color: rgba(0, 0, 0, 0%); font-family:'Courier';",
               "loc": [12,202],
               "size": [71, 22],
               "text": "ADD CHUM"
             },
  "pester": { "style": "background:  rgba(255, 255, 0, 0%); border:2px solid #c48a00; font: bold; color:  rgba(255, 255, 0, 0%); font-family:'Courier';",
               "loc": [150,202],
               "size": [71, 22],
               "text": "PESTER!"
             },
  "defaultmood": "chummy",
  "moodlabel": { "style": "",
				 "loc": [20, 4300],
				 "text": "MOODS"
			   },
  "moods": [
      { "style": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'", 
		"selected": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'; font:bold; font-size:9pt;",
		"loc": [12, 288],
		"size": [104, 22],
	    "text": "CHUMMY",
		"icon": "$path/chummy.gif",
		"mood": "chummy"
	  },
	  { "style": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'", 
		"selected": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'; font: bold; font-size:9pt;",
		"loc": [12, 308],
		"size": [104, 22],
		"text": "PALSY",
		"icon": "$path/chummy.gif",
		"mood": "pleasant.gif"
	  },
	  { "style": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'", 
		"selected": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier';font: bold; font-size:9pt;",
		"loc": [12, 328],
		"size": [104, 22],
		"text": "CHIPPER",
		"icon": "$path/chummy.gif",
		"mood": "distraught"
	  },
	  { "style": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'", 
		"selected": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'; font-size:9pt; font: bold;",
		"loc": [117, 288],
		"size": [104, 22],
		"text": "BULLY",
		"icon": "$path/chummy.gif",
		"mood": "unruly"
	  },
	  { "style": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier'", 
		"selected": "text-align:left; background: yellow; border:2px solid #c48a00; padding: 5px;color:#000000; font-family:'Courier';font: bold; font-size:9pt;",
		"loc": [117, 308],
		"size": [104, 22],
		"text": "PEPPY",
		"icon": "$path/chummy.gif",
		"mood": "smooth"
	  },
	  { "style": "text-align:left; background: red; border:2px solid #c48a00; padding: 5px;color:#FFFFFF; font-family:'Courier'", 
		"selected": "text-align:left; background: red; border:2px solid #c48a00; padding: 5px;color:#FFFFFF; font-family:'Courier';font: bold; font-size:9pt;",
		"loc": [117, 328],
		"size": [104, 22],
		"text": "RANCOROUS",
		"icon": "$path/rancorous.gif",
		"mood": 1
	  },
	  { "style": "text-align:center; background: black; border:2px solid #c48a00; padding: 5px;color:#646464; font-family:'Courier'", 
		"selected": "text-align:center; background: black; border:2px solid #c48a00; padding: 5px;color:#646464; font-family:'Courier';font: bold; font-size:9pt;",
		"loc": [12, 348],
		"size": [209, 22],
		"text": "ABSCOND",
		"icon": "$path/offline.gif",
		"mood": 2
	  }
  ]
 },
 "convo":
 {"style": "background: #fdb302; border:2px solid yellow; font-family: 'Courier'",
  "size": [295, 191],
  "chumlabel": { "style": "background: rgb(196, 138, 0);" },
  "textarea": {
      "style": "background: white; font:bold; border:2px solid #c48a00;"
  },
  "input": {
      "style": "background: white; border:2px solid #c48a00;"
  },
  "tabs": {
      "style": "",
      "newmsgcolor": "#fdb302",
      "tabstyle": 0
  }
 }
 
}
