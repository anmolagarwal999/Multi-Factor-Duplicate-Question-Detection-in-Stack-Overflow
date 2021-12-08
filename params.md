## For k = 20

### First 100 questions as training

- final best score: 0.78 with [0.39999999999999997, 0.49999999999999994, 0.13737961695900214, 0.19916776750438459] params

### First 300 questions as training

- Final best score: 0.74
- Params: [0.9000000000000002, 0.8500000000000002, 0.3152632209444808, 0.3]
  #### Test score
  - Final best score: 0.65

### Ablating Body

- Final Best Score: 0.7066666666666667

* Params: [1.0000000000000002, 0, 0.49999999999999994, 0.6]
  #### Testing
  - Final best score: 0.61

### Ablating Title

- Final Best Score: 0.61

* Params: [0, 0.8500000000000002, 0.35, 0.6434766392149411]
  #### Testing
  - Final best score: 0.53

### Ablating Tags

- Final Best Score: 0.67

* Params [0.9000000000000002, 0.8000000000000002, 0.1, 0]
  #### Testing
  - Final best score: 0.51

### Ablating Topics

- Final Best Score: 0.7333333333333333

* Params: [0.2, 0.19582983161315137, 0, 0.07184088591052762]
  #### Testing
  - Final best score: 0.61

### Adding jaccard score

- Final best score: 0.7633333333333333

* Params: [0.44999999999999996, 0.35, 0.25, 0.29413650364619237, 1.0000000000000002]
  #### Testing
  - Final best score: 0.65

### Bert Finetuning

- Bert Additional Params: [0.6, 0.5]

* Bert Improved Test Recall 0.88
* Bert Improved: Unique 20: 29, Richness: 32, RKO out of nowhere: 2

## K = 10

### First 100 questions as training

- Final best score: 0.74
- Params: [0.49999999999999994, 0.49999999999999994, 0.045457461811456046, 0.44999999999999996]
  #### Test score
  - Final best score: 

### First 300 questions as training

- Final best score: 0.67
- Params: [1.0000000000000002, 0.6, 0.3, 0.6]
  #### Test score
  - Final best score: 0.56

## Only one similarity used

### K = 20

### Only Title

- Params: [1, 0, 0, 0]
- Test score: 0.42

#### Only Body

- Params: [0, 1, 0, 0]
- Test score: 0.26

#### Only Topics

- Params: [0, 0, 1, 0]
- Test score: 0.14

#### Only Tags

- Params: [0, 0, 0, 1]
- Test score: 0.34

### K = 10

### Only Title

- Params: [1, 0, 0, 0]
- Test score: 0.33

#### Only Body

- Params: [0, 1, 0, 0]
- Test score: 0.2

#### Only Topics

- Params: [0, 0, 1, 0]
- Test score: 0.08

#### Only Tags

- Params: [0, 0, 0, 1]
- Test score: 0.28
