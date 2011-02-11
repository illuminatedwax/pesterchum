{"main":
 {"style": "background-repeat: no-repeat;",
  "background-image": "$path/pcbg.png",
  "size": [232, 380],
  "icon": "$path/trayicon.png",
  "newmsgicon": "$path/trayicon2.png",
  "windowtitle": "PESTERCHUM",
  "close": { "image": "$path/x.gif",
             "loc": [210, 2]},
  "minimize": { "image": "$path/m.gif",
                "loc": [194, 8]},
  "menubar": { "style": "font-family: 'Courier'; font:bold; font-size: 12px;" },
  "menu" : { "style": "font-family: 'Courier'; font: bold; font-size: 12px; background-color: #fdb302;border:2px solid #ffff00",
             "menuitem": "margin-right:10px;",
             "selected": "background-color: #ffff00",
             "loc": [10,0]
           },
  "sounds": { "alertsound": "$path/alarm.wav",
			  "ceasesound": "$path/cease.wav" },
  "menus": {"client": {"_name": "CLIENT",
                       "options": "OPTIONS",
                       "memos": "MEMOS",
                       "userlist": "USERLIST",
                       "import": "IMPORT",
					   "idle": "IDLE",
                       "exit": "EXIT"},
            "profile": {"_name": "PROFILE",
                        "switch": "SWITCH",
                        "color": "COLOR",
                        "theme": "THEME",
                        "block": "TROLLSLUM",
                        "quirks": "QUIRKS"},
            "help": { "_name": "HELP",
                      "about": "ABOUT" },
            "rclickchumlist": {"pester": "PESTER",
                               "removechum": "REMOVE CHUM",
                               "blockchum": "BLOCK",
                               "addchum": "ADD CHUM",
                               "unblockchum": "UNBLOCK",
                               "banuser": "BAN USER",
                               "opuser": "MAKE OP",
                               "quirksoff": "QUIRKS OFF"
                              }
           },
  "chums": { "style": "border:2px solid yellow; background-color: black;color: white;font: bold;font-family: 'Courier';selection-background-color:#646464; ",
             "loc": [12, 117],
             "size": [209, 82],
             "userlistcolor": "white",
             "moods": { 

                 "chummy": { "icon": "$path/chummy.gif", "color": "white" },

                 "rancorous": { "icon": "$path/rancorous.gif", "color": "red" },

                 "offline": { "icon": "$path/offline.gif", "color": "#646464"},

			     
                 "pleasant": { "icon": "$path/pleasant.gif", "color": "white" },

                 "distraught": { "icon": "$path/distraught.gif", "color": "white" },

                 "pranky": { "icon": "$path/pranky.gif", "color": "white" },


                 "smooth": { "icon": "$path/smooth.gif", "color": "white" },


                 "ecstatic": { "icon": "$path/ecstatic.gif", "color": "red" },

                 "relaxed": { "icon": "$path/relaxed.gif", "color": "red" },

                 "discontent": { "icon": "$path/discontent.gif", "color": "red" },

                 "devious": { "icon": "$path/devious.gif", "color": "red" },

                 "sleek": { "icon": "$path/sleek.gif", "color": "red" },
			     
                 "detestful": { "icon": "$path/detestful.gif", "color": "red" },

                 "mirthful": { "icon": "$path/mirthful.gif", "color": "red" },

                 "manipulative": { "icon": "$path/manipulative.gif", "color": "red" },

                 "vigorous": { "icon": "$path/vigorous.gif", "color": "red" },

                 "perky": { "icon": "$path/perky.gif", "color": "red" },

                 "acceptant": { "icon": "$path/acceptant.gif", "color": "red" },

                 "protective": { "icon": "$path/protective.gif", "color": "#00ff00" },

                 "blocked": { "icon": "$path/blocked.gif", "color": "black" }

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
                                "loc": [36,246],
                                "size": [190, 21] },
                    "colorswatch": { "loc": [196,246],
                                     "size": [23,21],
                                     "text": "" },
                    "currentMood": [18, 249]
                  },
  "defaultwindow": { "style": "background: #fdb302; font-family:'Courier';font:bold;selection-background-color:#919191; " 
                   },
  "addchum":  { "style": "background: rgba(255, 255, 0, 0%); border:2px solid #c48a00; font: bold; color: rgba(0, 0, 0, 0%); font-family:'Courier';",
                "loc": [12,202],
                "size": [71, 22],
                "text": ""
              },
  "pester": { "style": "background:  rgba(255, 255, 0, 0%); border:2px solid #c48a00; font: bold; color:  rgba(255, 255, 0, 0%); font-family:'Courier';",
              "pressed" : "background: rgb(255, 255, 255, 30%);",
              "loc": [150,202],
              "size": [71, 22],
              "text": ""
            },
  "block": { "style": "background:  rgba(255, 255, 0, 0%); border:2px solid #c48a00; font: bold; color:  rgba(255, 255, 0, 0%); font-family:'Courier';",
             "loc": [1500,202],
             "size": [0, 0],
             "text": ""
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
		"icon": "",
		"mood": 2
	  }
  ]
 },
 "convo":
 {"style": "background-color: #fdb302;background-image:url($path/convobg.png);background-repeat: no-repeat; border:2px solid yellow; font-family: 'Courier'",
  "tabstyle": "background-color: #fdb302; font-family: 'Courier'",
  "scrollbar": { "style" : "margin-right: 10px; padding-top:17px; padding-bottom:17px;width: 27px; background:white; border:2px solid #c48a00;",
                 "handle": "background-color:#c48a00;min-height:20px;",
                 "downarrow": "height:17px;border:2px solid #c48a00;", 
                 "darrowstyle": "image:url($path/downarrow.png);",
                 "uparrow": "height:17px;border:2px solid #c48a00;",
                 "uarrowstyle": "image:url($path/uparrow.png);"
               },
  "margins": {"top": 0, "bottom": 6, "left": 0, "right": 0 },
  "size": [520, 325],
  "chumlabel": { "style": "margin-bottom: 21px;background: rgb(196, 138, 0); color: white; border:0px; font-size: 14px;",
                 "align": { "h": "center", "v": "center" },
                 "minheight": 47,
                 "maxheight": 47,
                 "text" : ":: $handle ::"
               },
  "textarea": {
      "style": "background: white;  font-size: 14px;font:bold; border:2px solid #c48a00;text-align:center; margin-right:10px; margin-left:10px;"
  },
  "input": {
      "style": "background: white; border:2px solid #c48a00;margin-top:5px; margin-right:10px; margin-left:10px; font-size: 12px;"
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
      "unblocked": "unblocked",
	  "blockedmsg": "did not receive message from",
      "openmemo": "opened memo on board",
      "joinmemo": "responded to memo",
      "closememo": "ceased responding to memo",
      "kickedmemo": "You have been banned from this memo!",
	  "idle": "is now an idle chum!"
  },
  "systemMsgColor": "#646464"
 },
 "memos":
 {"memoicon": "$path/memo.png",
  "style": "background-color: #fdb302; background-image:url($path/convobg.png); background-repeat: no-repeat; border:2px solid yellow; font-family: 'Courier'; font: bold; selection-background-color:#919191; ",
  "size": [450,300],
  "tabs": {
      "style": "",
      "selectedstyle": "",
      "newmsgcolor": "#fdb302",
      "tabstyle": 0
  },
  "scrollbar": { "style" : "margin-right: 10px; padding-top:17px; padding-bottom:17px;width: 27px; background:white; border:2px solid #c48a00;",
                 "handle": "background-color:#c48a00;min-height:20px;",
                 "downarrow": "height:17px;border:2px solid #c48a00;", 
                 "darrowstyle": "image:url($path/downarrow.png);",
                 "uparrow": "height:17px;border:2px solid #c48a00;",
                 "uarrowstyle": "image:url($path/uparrow.png);"
               },
  "label": { "text": "Bulletin Board: $channel",
             "style": "margin-bottom: 21px;background: rgb(196, 138, 0); color: white; border:0px; font-size: 14px;",
             "align": { "h": "center", "v": "center" },
             "minheight": 47,
             "maxheight": 47
           },
  "input": { "style": "background: white; border:2px solid #c48a00;margin-top:5px; margin-right:10px; margin-left:10px; font-size: 12px;" },
  "textarea": { "style": "background: white;  font-size: 14px;font:bold; border:2px solid #c48a00;text-align:center; margin-right:10px; margin-left:10px;" },
  "margins": {"top": 0, "bottom": 6, "left": 0, "right": 0 },
  "userlist": { "width": 150,
                "style": "border:2px solid #c48a00; background: white;font: bold;font-family: 'Courier';selection-background-color:#646464; font-size: 12px;  margin-left:0px; margin-right:10px;"
              },
  "time": { "text": { "width": 75, 
                      "style": " border: 2px solid yellow; background: white; font-size: 12px; margin-top: 5px; margin-right: 5px; margin-left: 5px; font-family:'Courier';font:bold;" 
                    },
            "slider": { "style": "border: 0px;",
                        "groove": "",
                        "handle": ""
                      },
            "buttons": { "style": "color: black; font: bold; border: 2px solid #c48a00; font: bold; font-size: 12px; background: yellow; margin-top: 5px; margin-right: 5px; margin-left: 5px; padding: 2px; width: 50px;" }, 
            "arrows": { "left": "$path/leftarrow.png", 
                        "right": "$path/rightarrow.png",
                        "style": " border:0px; margin-top: 5px; margin-right:10px;" 
                      }
          },
  "systemMsgColor": "#646464",
  "op": { "icon": "$path/op.gif" }
 }
}