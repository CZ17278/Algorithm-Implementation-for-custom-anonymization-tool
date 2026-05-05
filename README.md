# CUSTOM ANONYMIZATION TOOL

## Overview

The **CUSTOM ANONYMIZATION TOOL** is a Python-based system designed to anonymize datasets while preserving data utility. It addresses the limitations of existing tools such as Amnesia (high information loss) and ARX (complex configuration), by providing an **automated, user-friendly, and adaptive anonymization process**.

The system supports:
- k-anonymity
- l-diversity
- t-closeness

---

## Key Features

- Automated generalization (no expert tuning required)
- Iterative anonymization strategy (levels 0–3)
- Integrated privacy validation
- Risk and utility evaluation
- Graphical User Interface (GUI)
- Designed for datasets up to 10,000 records

---

## System Architecture

The system follows a modular pipeline:

<img width="1984" height="247" alt="image" src="https://github.com/user-attachments/assets/dbe718ac-d906-4c59-a3c6-81461b5664eb" />


### Components

- **User Interface (Tkinter)**  
  Handles file upload, parameter selection, and execution

- **Preprocessing Module**  
  - Converts date of birth to age  
  - Removes direct identifiers (name, email)  
  - Cleans missing values  

- **Anonymization Engine**  
  - Applies generalization to quasi-identifiers  
  - Supports k-anonymity, l-diversity, t-closeness  
  - Iteratively increases generalization level  

- **Evaluation Module**  
  - Computes re-identification risk  
  - Computes information loss  

---

## Algorithm Implementation

### Core Logic

```python
def anonymize(df, qi, sensitive, method, k, l, t):

    for level in range(4):

        temp = apply_generalization(df, qi, level)

        if method == "k" and check_k(temp, qi, k):
            return temp, level

        elif method == "l" and check_l(temp, qi, sensitive, l):
            return temp, level

        elif method == "t" and check_t(temp, qi, sensitive, t):
            return temp, level

    return None

```
## Run
Run the application:
python custom anonymization tool.py

<img width="306" height="338" alt="image" src="https://github.com/user-attachments/assets/8acf602c-18b5-4068-b110-c68ebf47eacd" />

