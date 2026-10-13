# Golden 50 evaluation

The frozen production configuration classified review text only. Human labels were loaded only after inference for comparison.

- Label configuration: `ollama:qwen3.5:4b-q4_K_M@d8b0f5e9760c+enrich-v6-numeric-contract-rules+common-labels-v1+think-false`
- Reviews: 50
- Topic accuracy: 82.0%
- Topic macro F1: 0.629
- Intent accuracy: 78.0%
- Intent macro F1: 0.540
- Severity exact accuracy: 70.0%
- Severity MAE: 0.400
- Sentiment MAE: 0.331
- Needs-review accuracy: 80.0%
- Joint exact accuracy: 14.0%
- Rows with any disagreement: 43

## Disagreements

### 292ce26a-815d-4bce-a3b6-93cb6c9e7e2c

Fields: topic, sentiment, severity, needs_review

Review: Staff must be full of mentally ill kool-aid heads. Banning conservative music that speaks truth. Spotify is doing all they can to protect pedophiles, by banning Christian songs discussing the path the devil leads you down. Pride is a sin.

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "catalog"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -1.0, "severity": 1, "topic": "other"}`

### a70e8d3e-3f84-46bc-b008-67f476c67963

Fields: sentiment

Review: Great app use it every chance I get

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 991b6b3a-f511-458a-a5b7-234f78048fb5

Fields: sentiment

Review: Ads were okay, but limited functionality..it's just too much

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.5, "severity": 2, "topic": "usability"}`

### 0c6ca545-3f89-4da6-b3db-1a352371fb6e

Fields: sentiment, severity

Review: Hate this application 🤮🤮🤮🤮🤮🤮

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 1, "topic": "other"}`

### 111f9048-f7bd-4be0-813e-76b8fc49f73f

Fields: sentiment

Review: Excellent

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### b567f70c-edba-4922-ac2a-e945e5eb3472

Fields: sentiment

Review: good ❤❤🔊🔊

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.5, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### b5ee7834-a0eb-4c15-9c7b-935831021922

Fields: sentiment

Review: Spotify is awesome and and very diverse :)

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 1fc8b08f-7d6a-472f-b317-8ceb28d00f22

Fields: topic, sentiment

Review: Duo Premium .... No ads at all!

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "usability"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "billing"}`

### 947821dc-b356-45dc-a0bc-1903728fad40

Fields: sentiment, severity

Review: Very good but wen I play my song it o ly plays a little bit then it stops I updated my phone and it worked but it happend again they need to fix this issue

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 3, "topic": "playback"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.6, "severity": 4, "topic": "playback"}`

### 723f07de-9881-4049-8680-1a9e25652914

Fields: intent, sentiment, severity, needs_review

Review: Update: I reached out to Spotify Support and with some help from Sarah I was able to get the app working again. Old Post:Normally, the app works great, and I use it constantly. I tried to open it today, and it keeps crashing every time. I've tried uninstalling and reinstalling, and updating. Nothing seems to work unfortunately.

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 2, "topic": "playback"}`

Model: `{"intent": "cancellation", "needs_review": 1, "sentiment": -0.5, "severity": 4, "topic": "playback"}`

### 47428620-ec21-424d-a515-0b0b0012a5cf

Fields: sentiment

Review: This app is bad work

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.8, "severity": 2, "topic": "other"}`

### fc344263-308d-48a1-9715-c380d063b6de

Fields: sentiment

Review: Great...

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.5, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 6112667b-3d71-475c-b1a4-159b87f73d2b

Fields: sentiment

Review: Super

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 01d453b0-dca3-42e9-8aa4-5fc167b08070

Fields: sentiment

Review: I like it but god I hate it when the music Interrupts my ads

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.6, "severity": 2, "topic": "usability"}`

### ac6cd66d-a9d2-42a4-afb8-2f84beff7fd1

Fields: topic, intent, sentiment, severity, needs_review

Review: Lhat ng song nasa spotify

Human: `{"intent": "unclear", "needs_review": true, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.5, "severity": 2, "topic": "catalog"}`

### 44129679-31a0-4108-9314-086a3456f6ae

Fields: intent, sentiment

Review: Avtar sungh

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.8, "severity": 1, "topic": "other"}`

### 46842184-32f8-4088-ac15-2a700a7e94ed

Fields: topic, intent, sentiment, needs_review

Review: asem, lirik nya kdang gaada kek mana??

Human: `{"intent": "unclear", "needs_review": true, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "request", "needs_review": 0, "sentiment": -0.4, "severity": 1, "topic": "catalog"}`

### 657f1b77-0183-4b06-bf48-5e6d9ab08f9a

Fields: sentiment

Review: Hate This application 👎

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.9, "severity": 2, "topic": "other"}`

### 5de7f95b-ccad-41b2-9f63-a13f7c1d9f09

Fields: intent, sentiment, needs_review

Review: We are boycotting Swedish app in our protest against Sweden for their desrecpect & desceration of our holy book Qur'an

Human: `{"intent": "cancellation", "needs_review": false, "sentiment": -0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "unclear", "needs_review": 1, "sentiment": 0.0, "severity": 1, "topic": "other"}`

### de48c99b-46fe-4837-8634-e63dbc72a5ea

Fields: sentiment

Review: I LOVE that I was able to put in only a few songs I like and Spotify gave me recommendations for an AWESOME Playlist...!!!

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "catalog"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "catalog"}`

### 372d4e67-59cc-4c54-879f-3e8a202ee554

Fields: topic, intent, sentiment, severity, needs_review

Review: Please ye ads ko thoda kumm Karo harr ek song ke baad ad 🙏🙄

Human: `{"intent": "unclear", "needs_review": true, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.5, "severity": 2, "topic": "usability"}`

### 47f1406d-4918-4d60-9647-5ca8e610caca

Fields: sentiment

Review: Very poor updates as we cannot playback the songs and most bad updates are happening it is affecting the spotify quality

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 4, "topic": "playback"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.8, "severity": 4, "topic": "playback"}`

### 82780cbe-6435-4efb-84f6-8e5fa47ffc3a

Fields: sentiment

Review: Awesomeness 👌 👏 👍 😍 💖

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 36609c5c-fe48-4459-86b8-cc78fd3c77cd

Fields: intent, sentiment, severity

Review: Bheekhmangon

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.5, "severity": 2, "topic": "other"}`

### f4c8146a-d5c8-4168-b00e-21af666afc6a

Fields: intent, sentiment

Review: Unconditional love, Stoli Canales

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 3ddb3f4e-f7b9-430b-b335-eadc6d321f46

Fields: sentiment, severity, needs_review

Review: Deleting this App. The new update suck, we can't choose our fvrt songs after some clicks, we can't CHOOSE song after a song played, and we can't turn off shuffle option. They are pushing us to upgrade to Premium subscription. No wonder if you guys loose ratings and users. Anyway i am deleting this app after years of using.

Human: `{"intent": "cancellation", "needs_review": false, "sentiment": -1, "severity": 3, "topic": "billing"}`

Model: `{"intent": "cancellation", "needs_review": 1, "sentiment": -0.9, "severity": 4, "topic": "billing"}`

### 16d640e9-b281-4746-9562-c7dbcf7126b6

Fields: sentiment

Review: It's my best music app but now it's not...everything basic features is premium....

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 3, "topic": "billing"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.8, "severity": 3, "topic": "billing"}`

### 215463ae-95b7-4481-8747-1754b68f31fa

Fields: intent, sentiment, severity, needs_review

Review: What is happening with Spotify?? Recently I'm trying to play a song but it doesn't working. So I unstalled and thn again install it now I can't even open the app.. Just showing try again?? I really loved Spotify but this making me to rate it 1 star plz fix the problm as fast as u can

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 4, "topic": "playback"}`

Model: `{"intent": "unclear", "needs_review": 1, "sentiment": -0.9, "severity": 1, "topic": "playback"}`

### 46c0b49f-83a1-427e-8f0b-cef62e3c94b5

Fields: sentiment, severity

Review: Are you out of your mind? This is dangerous! Listening to music in a normal volume and suddenly an add starts and my ears feel like they explode!! Stop this BS, or you're gonna destroy someones ears.

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 4, "topic": "usability"}`

### 283b5843-a992-464f-b1dc-9dc7281ff390

Fields: topic, intent, needs_review

Review: Beth, we all got to give me a free dollar to go with 3 months, bro I can't be like

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "request", "needs_review": 1, "sentiment": 0.0, "severity": 1, "topic": "billing"}`

### 1d15724a-98ff-400a-8083-0d9afc801098

Fields: sentiment

Review: Good

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.7, "severity": 1, "topic": "other"}`

### 89ea724c-358f-48ab-9516-cd130d21c471

Fields: sentiment

Review: Good app!

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 2aa566c6-b98d-4513-b900-83702a8db8eb

Fields: sentiment

Review: Nice app, very less advertising

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "usability"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.01, "severity": 1, "topic": "usability"}`

### 8c0546b0-ce43-4a36-9d33-9f979e98d522

Fields: sentiment, severity

Review: 1-Lyrics not getting loaded, 2-can't go back to or start song where to wanted. Pathetic update

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 3, "topic": "catalog"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 4, "topic": "catalog"}`

### 8fd3dd72-5535-40f6-8779-1bd60892131e

Fields: sentiment

Review: Good

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.7, "severity": 1, "topic": "other"}`

### b58dd6f0-ad88-4319-b6db-58afb60c37c1

Fields: topic, sentiment

Review: The only thing Spotify lacks is the ability to organize saved 
albums/artists into collections. Would definitely deserve 5 stars if it 
included this feature.

Human: `{"intent": "request", "needs_review": false, "sentiment": 0.5, "severity": 1, "topic": "usability"}`

Model: `{"intent": "request", "needs_review": 0, "sentiment": 0.01, "severity": 1, "topic": "other"}`

### 1a41c7e1-a655-4c63-b4db-c22bdff18003

Fields: sentiment

Review: Worst application 👎👎👎

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 2, "topic": "other"}`

### dceb14e7-2df0-422f-bb2b-73d7c373159a

Fields: sentiment, severity

Review: I gave one star because I can't give any less than that. the new update is sooooooo annoying like I can't even play the songs that I like and I can't rewind songs what the heck

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 3, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 4, "topic": "usability"}`

### 5fba12ea-4980-4f25-a129-f830a3974fd2

Fields: topic, sentiment

Review: I find Spotify very good, it finds and play whatever music you want and also adds songs that you might like, judging from your playlist if you choose to arrange one. 😊💃🎸🎶

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "catalog"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.01, "severity": 1, "topic": "other"}`

### ac4e860a-c042-49cc-90f3-189591c336ac

Fields: topic, intent, sentiment, severity

Review: paying for subscribing but unable to play in offline mode really?

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 3, "topic": "downloads"}`

Model: `{"intent": "request", "needs_review": 0, "sentiment": -1.0, "severity": 1, "topic": "billing"}`

### 9034d675-9582-49b6-a1c1-c4ddabf8baf1

Fields: sentiment, severity

Review: Worst app ever too much ad

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 3, "topic": "usability"}`

### d2f3874f-d15d-4a2f-bb97-4f1213defa46

Fields: sentiment, severity

Review: Too expensive and the free version is pretty much unusable with constant ads... Every two or three songs.. Forget it

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 3, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.85, "severity": 4, "topic": "usability"}`

### 99b93e31-9f15-4daa-88ac-349ab0419c48

Fields: sentiment, needs_review

Review: This update very bad for everyone.old Spotify. we all want.

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.9, "severity": 2, "topic": "other"}`
