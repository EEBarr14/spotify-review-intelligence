# Jev Golden 50 evaluation

The frozen human answers were used only after model inference for comparison.

- Label configuration: `typesafe:jev-latest@2026-09-10T18:38:01.391457+00:00+spotify-contract-jev-v1-candidate+sentiment-score-v1+confidence-0.55`
- Topic accuracy: 88.0%
- Topic macro F1: 0.828
- Intent accuracy: 92.0%
- Intent macro F1: 0.790
- Severity exact accuracy: 86.0%
- Severity MAE: 0.160
- Sentiment MAE: 0.222
- Needs-review accuracy: 50.0%
- Joint exact accuracy: 4.0%
- Rows with any disagreement: 48

## Disagreements

### 292ce26a-815d-4bce-a3b6-93cb6c9e7e2c

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "catalog"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.995, "severity": 2, "topic": "catalog"}`

### a70e8d3e-3f84-46bc-b008-67f476c67963

Fields: sentiment

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.985, "severity": 1, "topic": "other"}`

### 991b6b3a-f511-458a-a5b7-234f78048fb5

Fields: sentiment, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.415, "severity": 2, "topic": "usability"}`

### 599a0d41-989a-40ef-8ed2-e92db76eea46

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 1, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.99, "severity": 1, "topic": "other"}`

### 0c6ca545-3f89-4da6-b3db-1a352371fb6e

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 2, "topic": "other"}`

### 111f9048-f7bd-4be0-813e-76b8fc49f73f

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.975, "severity": 1, "topic": "other"}`

### b567f70c-edba-4922-ac2a-e945e5eb3472

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.5, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.68, "severity": 1, "topic": "other"}`

### b5ee7834-a0eb-4c15-9c7b-935831021922

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.885, "severity": 1, "topic": "other"}`

### 1fc8b08f-7d6a-472f-b317-8ceb28d00f22

Fields: sentiment

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "usability"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.725, "severity": 1, "topic": "usability"}`

### 947821dc-b356-45dc-a0bc-1903728fad40

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 3, "topic": "playback"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.3, "severity": 3, "topic": "playback"}`

### 723f07de-9881-4049-8680-1a9e25652914

Fields: sentiment, severity, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 2, "topic": "playback"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": 0.365, "severity": 4, "topic": "playback"}`

### 47428620-ec21-424d-a515-0b0b0012a5cf

Fields: sentiment, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.66, "severity": 2, "topic": "other"}`

### fc344263-308d-48a1-9715-c380d063b6de

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.5, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.385, "severity": 1, "topic": "other"}`

### 6112667b-3d71-475c-b1a4-159b87f73d2b

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.825, "severity": 1, "topic": "other"}`

### 01d453b0-dca3-42e9-8aa4-5fc167b08070

Fields: sentiment, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.25, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.135, "severity": 2, "topic": "usability"}`

### ac6cd66d-a9d2-42a4-afb8-2f84beff7fd1

Fields: topic, sentiment

Human: `{"intent": "unclear", "needs_review": true, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "unclear", "needs_review": 1, "sentiment": -0.005, "severity": 1, "topic": "catalog"}`

### 44129679-31a0-4108-9314-086a3456f6ae

Fields: sentiment, needs_review

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "unclear", "needs_review": 1, "sentiment": 0.085, "severity": 1, "topic": "other"}`

### 46842184-32f8-4088-ac15-2a700a7e94ed

Fields: topic, intent, sentiment, severity

Human: `{"intent": "unclear", "needs_review": true, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.34, "severity": 2, "topic": "catalog"}`

### 657f1b77-0183-4b06-bf48-5e6d9ab08f9a

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.965, "severity": 2, "topic": "other"}`

### 5de7f95b-ccad-41b2-9f63-a13f7c1d9f09

Fields: intent, sentiment, severity

Human: `{"intent": "cancellation", "needs_review": false, "sentiment": -0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "unclear", "needs_review": 0, "sentiment": -0.99, "severity": 2, "topic": "other"}`

### de48c99b-46fe-4837-8634-e63dbc72a5ea

Fields: sentiment

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "catalog"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 1.0, "severity": 1, "topic": "catalog"}`

### 372d4e67-59cc-4c54-879f-3e8a202ee554

Fields: topic, intent, sentiment, severity

Human: `{"intent": "unclear", "needs_review": true, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "request", "needs_review": 1, "sentiment": -0.525, "severity": 2, "topic": "usability"}`

### 47f1406d-4918-4d60-9647-5ca8e610caca

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 4, "topic": "playback"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.99, "severity": 4, "topic": "playback"}`

### 82780cbe-6435-4efb-84f6-8e5fa47ffc3a

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 1.0, "severity": 1, "topic": "other"}`

### 36609c5c-fe48-4459-86b8-cc78fd3c77cd

Fields: sentiment, needs_review

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "unclear", "needs_review": 1, "sentiment": -0.045, "severity": 1, "topic": "other"}`

### f4c8146a-d5c8-4168-b00e-21af666afc6a

Fields: intent, sentiment, needs_review

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.89, "severity": 1, "topic": "other"}`

### 3ddb3f4e-f7b9-430b-b335-eadc6d321f46

Fields: topic, sentiment

Human: `{"intent": "cancellation", "needs_review": false, "sentiment": -1, "severity": 3, "topic": "billing"}`

Model: `{"intent": "cancellation", "needs_review": 0, "sentiment": -0.995, "severity": 3, "topic": "usability"}`

### 16d640e9-b281-4746-9562-c7dbcf7126b6

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 3, "topic": "billing"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.53, "severity": 3, "topic": "billing"}`

### 8cc4fad4-26ec-47b7-96e8-49c7da714eca

Fields: sentiment, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.705, "severity": 2, "topic": "other"}`

### 215463ae-95b7-4481-8747-1754b68f31fa

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 4, "topic": "playback"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.955, "severity": 4, "topic": "playback"}`

### 46c0b49f-83a1-427e-8f0b-cef62e3c94b5

Fields: sentiment, severity, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -1.0, "severity": 3, "topic": "usability"}`

### 283b5843-a992-464f-b1dc-9dc7281ff390

Fields: topic, sentiment, needs_review

Human: `{"intent": "unclear", "needs_review": false, "sentiment": 0, "severity": 1, "topic": "other"}`

Model: `{"intent": "unclear", "needs_review": 1, "sentiment": -0.29, "severity": 1, "topic": "billing"}`

### 1d15724a-98ff-400a-8083-0d9afc801098

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.5, "severity": 1, "topic": "other"}`

### 89ea724c-358f-48ab-9516-cd130d21c471

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.54, "severity": 1, "topic": "other"}`

### 2aa566c6-b98d-4513-b900-83702a8db8eb

Fields: sentiment

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "usability"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.53, "severity": 1, "topic": "usability"}`

### 8c0546b0-ce43-4a36-9d33-9f979e98d522

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 3, "topic": "catalog"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.975, "severity": 3, "topic": "catalog"}`

### a972945c-6601-4108-882a-afe986866a7b

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 1, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.995, "severity": 1, "topic": "other"}`

### 8fd3dd72-5535-40f6-8779-1bd60892131e

Fields: sentiment, needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.25, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 0.5, "severity": 1, "topic": "other"}`

### b58dd6f0-ad88-4319-b6db-58afb60c37c1

Fields: sentiment

Human: `{"intent": "request", "needs_review": false, "sentiment": 0.5, "severity": 1, "topic": "usability"}`

Model: `{"intent": "request", "needs_review": 0, "sentiment": 0.245, "severity": 1, "topic": "usability"}`

### 1a41c7e1-a655-4c63-b4db-c22bdff18003

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 2, "topic": "other"}`

### dceb14e7-2df0-422f-bb2b-73d7c373159a

Fields: sentiment, severity, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 3, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.985, "severity": 4, "topic": "usability"}`

### 5fba12ea-4980-4f25-a129-f830a3974fd2

Fields: sentiment

Human: `{"intent": "praise", "needs_review": false, "sentiment": 0.75, "severity": 1, "topic": "catalog"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.85, "severity": 1, "topic": "catalog"}`

### ac4e860a-c042-49cc-90f3-189591c336ac

Fields: sentiment, severity, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.5, "severity": 3, "topic": "downloads"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.56, "severity": 4, "topic": "downloads"}`

### 9034d675-9582-49b6-a1c1-c4ddabf8baf1

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -1.0, "severity": 2, "topic": "usability"}`

### d2f3874f-d15d-4a2f-bb97-4f1213defa46

Fields: topic, sentiment, needs_review

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 3, "topic": "usability"}`

Model: `{"intent": "complaint", "needs_review": 1, "sentiment": -0.95, "severity": 3, "topic": "billing"}`

### 99b93e31-9f15-4daa-88ac-349ab0419c48

Fields: sentiment

Human: `{"intent": "complaint", "needs_review": false, "sentiment": -0.75, "severity": 2, "topic": "other"}`

Model: `{"intent": "complaint", "needs_review": 0, "sentiment": -0.96, "severity": 2, "topic": "other"}`

### ca63dfbe-7120-4e18-af6e-8ea786cd157d

Fields: sentiment

Human: `{"intent": "praise", "needs_review": false, "sentiment": 1, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 0, "sentiment": 0.89, "severity": 1, "topic": "other"}`

### 083811c7-d469-499b-9bef-5b9fb096653d

Fields: needs_review

Human: `{"intent": "praise", "needs_review": false, "sentiment": 1, "severity": 1, "topic": "other"}`

Model: `{"intent": "praise", "needs_review": 1, "sentiment": 1.0, "severity": 1, "topic": "other"}`
