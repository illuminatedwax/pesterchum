{"inherits": "pesterchum",
 "main":
 {"style": "",
  "background-image": "$path/pcbg.png",
  "size": [300,620],
  "icon": "$path/trayicon.png",
  "newmsgicon": "$path/trayicon2.png",
  "windowtitle": "PESTERCHUM",
  "menu" : { "style": "font-family: 'Courier'; font: bold; font-size: 14px; background-color: #fdb302;border:2px solid #ffff00",
			 "menuitem": "font-size:14px;" },
  "close": { "image": "$path/x.gif",
             "loc": [280, 2]},
  "minimize": { "image": "$path/m.gif",
                "loc": [260, 8]},
  "chums": { "style": "border:2px solid yellow; background-color: black;color: white;font: bold;font-size:14px;font-family: 'Courier';selection-background-color:#646464; ",
			 "loc": [15, 70],
			 "size": [270, 300]
           },
  "mychumhandle": { "label": 
                    { "text": "CHUMHANDLE:",
                      "loc": [12,415],
                      "style": "color: black ;font:bold; font-family: 'Courier';" 
                    },
                    "handle": { "loc": [15,435],
                                "size": [240, 21],
								"style": "background-color: black; padding: 3px; padding-left: 20px; color:white; font-family:'Courier'; font:bold; text-align:left;"
							  },
                    "colorswatch": { "loc": [260,435],
                                     "size": [30,30],
                                     "text": "C" },
                    "currentMood": [15, 435]
                  },
  "addchum":  { "style": "background: rgba(255, 255, 0, 100%); border:2px solid #c48a00; font: bold; color: black; font-family:'Courier';",
                "loc": [15,380],
                "size": [90, 30],
                "text": "ADD CHUM"
              },
  "pester": { "style": "background:  rgba(255, 255, 0, 100%); border:2px solid #c48a00; font: bold; color: black; font-family:'Courier';",
              "loc": [193,380],
              "size": [89, 30],
              "text": "PESTER!"
            },
  "block": { "style": "background: #F00000; border:2px solid #c48a00; font: bold; color: black; font-family:'Courier';",
             "loc": [104,380],
             "size": [89, 30],
             "text": "BLOCK"
           },
  "moodlabel": { "style": "font:bold;font-family:'Courier';color:black;",
				 "loc": [20, 460],
				 "text": "MOODS:"
			   },
  "moods": [
      { "style": "text-align:left; background:#ffff00;border:2px solid #c48a00;color: black; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; color: black; font-family:'Courier'; font:bold;",
		"loc": [15, 480],
		"size": [135, 30],
	    "text": "CHUMMY",
		"icon": "$path/chummy.gif",
		"mood": 0
	  },

      { "style": "text-align:left; background:#ffff00;border:2px solid #c48a00;color: black; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; color: black; font-family:'Courier'; font:bold;",
		"loc": [15, 508],
		"size": [135, 30],
	    "text": "PLEASANT",
		"icon": "$path/pleasant.gif",
		"mood": 3
	  },

      { "style": "text-align:left; background:#ffff00;border:2px solid #c48a00;color: black; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; color: black; font-family:'Courier'; font:bold;",
		"loc": [15, 536],
		"size": [135, 30],
	    "text": "DISTRAUGHT",
		"icon": "$path/distraught.gif",
		"mood": 4
	  },

      { "style": "text-align:left; background:#ffff00;border:2px solid #c48a00;color: black; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; color: black; font-family:'Courier'; font:bold;",
		"loc": [148, 480],
		"size": [135, 30],
	    "text": "PRANKY",
		"icon": "$path/pranky.gif",
		"mood": 5
	  },

      { "style": "text-align:left; background:#ffff00;border:2px solid #c48a00;color: black; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; color: black; font-family:'Courier'; font:bold;",
		"loc": [148, 508],
		"size": [135, 30],
	    "text": "SMOOTH",
		"icon": "$path/smooth.gif",
		"mood": 6
	  },

      { "style": "text-align:left; background:#f00000;border:2px solid #c48a00;color: black; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; color: red; font-family:'Courier'; font:bold;",
		"loc": [148, 536],
		"size": [135, 30],
	    "text": "RANCOROUS",
		"icon": "$path/rancorous.gif",
		"mood": 1
	  },

      { "style": "text-align:center; border:2px solid #c48a00; background:black;color: white; font-family:'Courier'; font:bold;", 
		"selected": "text-align:left; background:white; border:2px solid #c48a00; padding: 5px;color: black; font-family:'Courier'; font:bold;",
		"loc": [15, 564],
		"size": [270, 30],
		"text": "ABSCOND",
		"icon": "$path/offline.gif",
		"mood": 2
	  }
  ]
 }
}



  