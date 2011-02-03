{"main":
 {"style": "background-image:url($path/tnbg.png);background-color:rgba(255,255,255,0);",
  "size": [650, 450],
  "icon": "$path/trayicon.png",
  "newmsgicon": "$path/trayicon2.png",
  "windowtitle": "TROLLIAN",
  "close": { "image": "$path/x.gif",
             "loc": [635, 2]},
  "minimize": { "image": "$path/m.gif",
                "loc": [621, 8]},
  "menubar": { "style": "font-family: 'Arial'; font-size: 11px; color: rgba(0,0,0,0);" },
  "menu" : { "style": "font-family: 'Arial'; font-size: 11px; background-color: #c2c2c2; border:1px solid #545454;",
  "selected": "background-color: #545454",
   "menuitem": "margin-right:14px;",
   	"loc": [14,90]
           },
  "sounds": { "alertsound": "$path/alarm.wav" },
  "menus": {"client": {"_name": "Trollian",
                       "options": "Options",
                       "userlist": "Fresh Targets",
                       "exit": "Abscond"},
            "profile": {"_name": "View",
                        "switch": "Trolltag",
                        "theme": "Theme",
                        "color": "Hemospectrum",
                        "block": "Chumpdump",
                        "quirks": "Annoying"},
            "rclickchumlist": {"pester": "Troll",
                               "removechum": "Trash",
                               "blockchum": "Block",
                               "addchum": "Add Chump",
                               "unblockchum": "Mercy"}
           },
  "chums": { "style": "border: 0px; background-color: white; padding: 5px; font-family: 'Arial';selection-background-color:rgb(200,200,200); ",
             "loc": [476, 90],
             "size": [175, 361],
             "userlistcolor": "black",
             "moods": { 

"chummy": { "icon": "$path/chummy.png", "color": "#63ea00" },

"rancorous": { "icon": "$path/rancorous.png", "color": "#7f7f7f" },

"offline": { "icon": "$path/offline.png", "color": "black"},

			
"pleasant": { "icon": "$path/pleasant.png", "color": "#d69df8" },

"distraught": { "icon": "$path/distraught.png", "color": "#706eba" },

"unruly": { "icon": "$path/unruly.png", "color": "blue" },


"smooth": { "icon": "$path/smooth.png", "color": "red" },


"ecstatic": { "icon": "$path/ecstatic.png", "color": "#99004d" },

"relaxed": { "icon": "$path/relaxed.png", "color": "#078446" },

"discontent": { "icon": "$path/discontent.png", "color": "#a75403" },

"devious": { "icon": "$path/devious.png", "color": "#008282" },

"sleek": { "icon": "$path/sleek.png", "color": "#a1a100" },
			
"detestful": { "icon": "$path/detestful.png", "color": "#6a006a" },

"mirthful": { "icon": "$path/mirthful.png", "color": "#450077" },

"manipulative": { "icon": "$path/manipulative.png", "color": "#004182" },

"vigorous": { "icon": "$path/vigorous.png", "color": "#0021cb" },

"perky": { "icon": "$path/perky.png", "color": "#406600" },

"acceptant": { "icon": "$path/acceptant.png", "color": "#a10000" },

"protective": { "icon": "$path/protective.png", "color": "white" },

"blocked": { "icon": "$path/blocked.png", "color": "black" }
					
                      }
           },
  "trollslum": { 
      "style": "background:  rgb(190, 19, 4); font-family: 'Arial'",
      "size": [175, 461],
      "label": { "text": "Chumpdump",
                 "style": "color: rgba(0, 0, 0, 100%) ;font:bold; font-family: 'Arial';border: 0px;" },
      "chumroll": {"style": "border: 0px; background-color: white; padding: 5px; font-family: 'Arial';selection-background-color:rgb(200,200,200); " }
  },
  "mychumhandle": { "label": { "text": "",
                               "loc": [85,410],
                               "style": "color:rgba(0,0,0,0);" },
                    "handle": { "style": "background: rgba(0,0,0,0); color:rgba(0,0,0,0);",
                                "loc": [0,0],
                                "size": [0,0] },
                    "colorswatch": { "loc": [0,0],
                                     "size": [0,0],
                                     "text": "" }
                  },
  "defaultwindow": { "style": "background: #c2c2c2; font-family:'Arial';font:bold;selection-background-color:#545454; " 
                   },
  "addchum": { "style": "background: rgba(0,0,0,0); border:0px; color: rgba(0,0,0,0);",
               "loc": [475, 67],
               "size": [175, 18],
               "text": ""
             },
  "pester": { "style": "background: rgba(0,0,0,0); border:0px; color: rgba(0,0,0,0);",
               "loc": [0,0],
               "size": [0, 0],
               "text": ""
             },
  "block": { "style": "background: rgba(0,0,0,0); border:0px; color: rgba(0,0,0,0);",
               "loc": [1500,202],
               "size": [71, 22],
               "text": ""
             },
  "defaultmood": 7,
  "moodlabel": { "style": "",
				 "loc": [0, 0],
				 "text": ""
			   },
  "moods": [
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck1.png); border:0px;",
		"loc": [25, 141],
		"size": [20, 270],
	    "text": "",
		"icon": "",
		"mood": 17
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck2.png); border:0px;",
		"loc": [60, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 9
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck3.png); border:0px;",
		"loc": [95, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 11
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck4.png); border:0px;",
		"loc": [130, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 1
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck5.png); border:0px;",
		"loc": [165, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 16
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck6.png); border:0px;",
		"loc": [200, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 8
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck7.png); border:0px;",
		"loc": [235, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 10
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck8.png); border:0px;",
		"loc": [270, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 14
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck9.png); border:0px;",
		"loc": [305, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 15
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck10.png); border:0px;",
		"loc": [340, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 13
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck11.png); border:0px;",
		"loc": [375, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 12
	  },
                { "style": "border:0px;", 
		"selected": "background-image:url($path/moodcheck12.png); border:0px;",
		"loc": [410, 141],
		"size": [20, 270],
		"text": "",
		"icon": "",
		"mood": 7
	  },

                { "style": "border:0px;color: rgba(0, 0, 0, 0%);", 
		"selected": "border:0px; color: rgba(0, 0, 0, 0%);",
		"loc": [12, 117],
		"size": [435, 18],
		"text": "",
		"icon": "",
		"mood": 2
	  }
  ]
 },
 "convo":
 {"style": "background:  rgb(190, 19, 4); font-family: 'Arial';",
  "size": [308, 194],
  "chumlabel": { "style": "background: rgb(255, 38, 18); color: white;",
                 "align": { "h": "center", "v": "center" },
                 "minheight": 30,
                 "maxheight": 50,
                 "text" : "trolling: $handle" 
               },
  "textarea": {
      "style": "background: white; border:0px;"
  },
  "input": {
      "style": "background: white; border:0px solid #c48a00;margin-top:5px;"
  },
  "tabs": {
      "style": "",
      "selectedstyle": "",
      "newmsgcolor": "red",
      "tabstyle": 0
  },
  "text": {
      "beganpester": "began trolling",
      "ceasepester": "gave up trolling",
      "blocked": "blocked",
      "unblocked": "mercifully forgave"
  },
  "systemMsgColor": "#646464"
 }
 
}