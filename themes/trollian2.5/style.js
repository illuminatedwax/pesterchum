{"inherits": "pesterchum2.5",
 "main":
 {"background-image": "$path/tnbg2.png",
  "size": [300,620],
  "icon": "$path/trayicon.png",
  "newmsgicon": "$path/trayicon2.png",
  "windowtitle": "TROLLIAN",
  "menu" : { "style": "font-family: 'Arial'; font: bold; font-size: 14px; background-color: #e5000f;border:2px solid #c20f00" },
  "close": { "image": "$path/x.gif",
             "loc": [280, 2]},
  "minimize": { "image": "$path/m.gif",
                "loc": [260, 8]},
  "defaultwindow": { "style": "background: #e5000f; font-family:'Arial';font:bold;selection-background-color:#919191; " },
  "chums": { "style": "border:2px solid #ffa4a4; background-color: black;color: white;font: bold;font-size:14px;font-family: 'Arial';selection-background-color:#646464; " },
  "mychumhandle": { "label": 
                    { "text": "TROLLTAG:",
                      "style": "color: black ;font:bold; font-family: 'Arial';" 
                    },
					"handle": { "style": "background-color: black; padding: 3px; padding-left: 25px; color:white; font-family:'Arial'; font:bold; text-align:left; border:2px solid #ffa4a4;" }
                  },
  "addchum":  { "style": "background: #ffa4a4; border:2px solid #780000; font: bold; color: black; font-family:'Arial';"
              },
  "pester": { "style": "background: #ffa4a4; border:2px solid #780000; font: bold; color: black; font-family:'Arial';"
            },
  "block": { "style": "background: #ffa4a4; border:2px solid #780000; font: bold; color: black; font-family:'Arial';"
           },
  "moodlabel": { "style": "font:bold;font-family:'Arial';color:black;"
			   },
  "defaultmood": 7,
  "moods": [
      { "style": "text-align:left; background:#ffa4a4;border:2px solid #780000;color: black; font-family:'Arial'; font:bold; padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; color: black; font-family:'Arial'; font:bold; padding-left:3px;",
		"loc": [15, 485],
		"size": [135, 30],
	    "text": "ECSTATIC",
		"icon": "$path/estatic.gif",
		"mood": 7
	  },

      { "style": "text-align:left; background:#ffa4a4;border:2px solid #780000;color: black; font-family:'Arial'; font:bold; padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; color: black; font-family:'Arial'; font:bold; padding-left:3px;",
		"loc": [15, 513],
		"size": [135, 30],
	    "text": "RELAXED",
		"icon": "$path/relaxed.gif",
		"mood": 8
	  },

      { "style": "text-align:left; background:#ffa4a4;border:2px solid #780000;color: black; font-family:'Arial'; font:bold; padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; color: black; font-family:'Arial'; font:bold; padding-left:3px;",
		"loc": [15, 541],
		"size": [135, 30],
	    "text": "DISCONTENT",
		"icon": "$path/discontent.gif",
		"mood": 9
	  },

      { "style": "text-align:left; background:#ffa4a4;border:2px solid #780000;color: black; font-family:'Arial'; font:bold; padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; color: black; font-family:'Arial'; font:bold; padding-left:3px;",
		"loc": [148, 485],
		"size": [135, 30],
	    "text": "DEVIOUS",
		"icon": "$path/devious.gif",
		"mood": 10
	  },

      { "style": "text-align:left; background:#ffa4a4;border:2px solid #780000;color: black; font-family:'Arial'; font:bold; padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; color: black; font-family:'Arial'; font:bold; padding-left:3px;",
		"loc": [148, 513],
		"size": [135, 30],
	    "text": "SLEEK",
		"icon": "$path/sleek.gif",
		"mood": 11
	  },

      { "style": "text-align:left; background:#ffa4a4;border:2px solid #780000;color: black; font-family:'Arial'; font:bold; padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; color: black; font-family:'Arial'; font:bold; padding-left:3px;",
		"loc": [148, 541],
		"size": [135, 30],
	    "text": "DETESTFUL",
		"icon": "$path/detestful.gif",
		"mood": 12
	  },

      { "style": "text-align:center; border:2px solid #780000; background:black;color: white; font-family:'Arial'; font:bold;padding-left:3px;", 
		"selected": "text-align:left; background:white; border:2px solid #780000; padding: 5px;color: black; font-family:'Arial'; font:bold;padding-left:3px;",
		"loc": [15, 569],
		"size": [270, 30],
		"text": "ABSCOND",
		"icon": "$path/offline.gif",
		"mood": 2
	  }
  ]
 },
 "convo": {
     "style": "background-color: #e5000f;border:2px solid #780000; font-family: 'Arial';",
     "chumlabel": { "style": "margin-bottom: 21px;background: #ffa4a4; color: black; border:0px; font-size: 14px;",
					"text" : ":: trolling: $handle ::" },
	 "textarea": {
		 "style": "background: white;  font-size: 14px;font:bold; border:2px solid #ffa4a4;text-align:center; margin-right:10px; margin-left:10px;font-family: 'Arial'"
	 },
	 "tabwindow" : {
		 "style": ""
	 },
	 "tabs": {
		 "style": "",
		 "selectedstyle": "",
		 "newmsgcolor": "#ff0000"
	 },
	 "scrollbar": null
 },
 "memos":
 { "size": [600,425],
   "style": "background-color: #e5000f;border:2px solid #780000; font-family: 'Arial';",
   "label": { "style": "margin-bottom: 21px;background: #ffa4a4; color: white; border:0px; font-size: 14px;"
			},
   "textarea": {
	   "style": "background: white;  font-size: 14px;font:bold; border:2px solid #ffa4a4;text-align:center; margin-right:10px; margin-left:10px;font-family: 'Arial'"
   },
   "userlist": { "style": "border:2px solid #780000; background: white;font: bold;font-family: 'Courier';selection-background-color:#646464; font-size: 12px;  margin-left:0px; margin-right:10px;"
               },
   "input": { "style": "background: white; border:2px solid #ffa4a4;margin-top:5px; margin-right:10px; margin-left:10px; font-size: 12px;" },
   "time": { "text": { "style": " border: 2px solid #780000; background: white; font-size: 12px; margin-top: 5px; margin-right: 5px; margin-left: 5px; font-family:'Arial';font:bold;" 
                    },
             "buttons": { "style": "color: black; font: bold; border: 2px solid #780000; font: bold; font-size: 12px; background: #e5000f; margin-top: 5px; margin-right: 5px; margin-left: 5px; padding: 2px; width: 50px;" }
          },

   "tabs": {
       "style": "",
       "selectedstyle": "",
       "newmsgcolor": "#ff0000",
       "tabstyle": 0
   },
   "scrollbar": null
 }
}
