{"main":
 {"style": "background-image:url($path/pcbg.png);",
  "size": [232, 380],
  "icon": "$path/trayicon.png",
  "newmsgicon": "$path/trayicon2.png",
  "windowtitle": "PESTERCHUM",
  "close": { "image": "$path/x.gif",
             "loc": [210, 2]},
  "minimize": { "image": "$path/m.gif",
                "loc": [190, 2]},
  "menubar": { "style": "font-family: 'Courier'; font:bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier'; font: bold; font-size: 12px; background-color: #fdb302;border:2px solid #ffff00",
             "menuitem": "margin-right:10px;",
             "selected": "background-color: #ffff00",
             "loc": [10,0]
           },
  "sounds": { "alertsound": "$path/alarm.wav" },
  "menus": {"client": {"_name": "CLIENT",
                       "options": "OPTIONS",
                       "exit": "EXIT"},
            "profile": {"_name": "PROFILE",
                        "switch": "SWITCH",
                        "color": "COLOR",
                        "theme": "THEME",
                        "block": "TROLLSLUM",
                        "quirks": "QUIRKS"},
            "rclickchumlist": {"pester": "PESTER",
                               "removechum": "REMOVE CHUM",
                               "blockchum": "BLOCK",
                               "unblockchum": "UNBLOCK"
                              }
           },
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
									"color": "white" },
                        "blocked": { "icon": "$path/blocked.gif",
                                     "color": "black" }
                      }
           },
  "trollslum": { 
      "style": "background: #fdb302; border:2px solid yellow; font-family: 'Courier'",
      "size": [195, 200],
      "label": { "text": "TROLLSLUM",
                 "style": "color: rgba(0, 0, 0, 100%) ;font:bold; font-family: 'Courier';border:0px;" },
      "chumroll": {"style": "border:2px solid yellow; background-color: black;color: white;font: bold;font-family: 'Courier';selection-background-color:#646464; " }
  },
  "mychumhandle": { "label": { "text": "CHUMHANDLE:",
                               "loc": [19,232],
                 "style": "color: rgba(255, 255, 0, 0%) ;font:bold; font-family: 'Courier';" },
                    "handle": { "style": "background: black; padding: 3px; color:white; font-family:'Courier'; font:bold; text-align:left;",
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
  "block": { "style": "background:  rgba(255, 255, 0, 0%); border:2px solid #c48a00; font: bold; color:  rgba(255, 255, 0, 0%); font-family:'Courier';",
               "loc": [1500,202],
               "size": [0, 0],
               "text": "BLOCK"
             },
  "defaultmood": 0,
  "moodlabel": { "style": "",
				 "loc": [20, 430],
				 "text": "MOODS"
			   },
  "moods": [
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck1.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [12, 288],
		"size": [104, 22],
	    "text": "CHUMMY",
		"icon": "$path/chummy.gif",
		"mood": 0
	  },
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck2.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [12, 308],
		"size": [104, 22],
		"text": "PALSY",
		"icon": "$path/chummy.gif",
		"mood": 3
	  },
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck3.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [12, 328],
		"size": [104, 22],
		"text": "CHIPPER",
		"icon": "$path/chummy.gif",
		"mood": 4
	  },
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck2.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [117, 288],
		"size": [104, 22],
		"text": "BULLY",
		"icon": "$path/chummy.gif",
		"mood": 5
	  },
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck2.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [117, 308],
		"size": [104, 22],
		"text": "PEPPY",
		"icon": "$path/chummy.gif",
		"mood": 6
	  },
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck4.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [117, 328],
		"size": [104, 22],
		"text": "RANCOROUS",
		"icon": "$path/rancorous.gif",
		"mood": 1
	  },
                { "style": "text-align:left; border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier'", 
		"selected": "text-align:left; background-image:url($path/moodcheck5.gif); border:2px solid #c48a00; padding: 5px;color: rgba(0, 0, 0, 0%); font-family:'Courier';",
		"loc": [12, 348],
		"size": [209, 22],
		"text": "ABSCOND",
		"icon": "$path/x.gif",
		"mood": 2
	  }
  ]
 },
 "convo":
 {"style": "background: #fdb302; border:2px solid yellow; font-family: 'Courier'",
  "size": [295, 191],
  "chumlabel": { "style": "background: rgb(196, 138, 0); color: white; border:0px;",
                 "align": { "h": "center", "v": "center" },
                 "minheight": 30,
                 "maxheight": 50,
                 "text" : ":: $handle ::"
               },
  "textarea": {
      "style": "background: white; font:bold; border:2px solid #c48a00;text-align:center;"
  },
  "input": {
      "style": "background: white; border:2px solid #c48a00;margin-top:5px;"
  },
  "tabs": {
      "style": "",
      "selectedstyle": "",
      "newmsgcolor": "#fdb302",
      "tabstyle": 0
  },
  "text": {
      "beganpester": "began pestering",
      "ceasepester": "ceased pestering",
      "blocked": "blocked",
      "unblocked": "unblocked"
  },
  "systemMsgColor": "#646464"
 }
 
}