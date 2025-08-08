# Project Plan: AI/ML Enhancement for FortiGate API Client

## 1. User Instructions

The user has provided the following instructions:

> Please review my app to understand it. This is an app that was initially just to provide a front end for easier usability to the pyfgt module for making rest API querieis to fortigate firewalls and formatting results as requested. We then added some ai/ml functionality to it to try to add natural language querying as well as ai intelligent formatted output. We added an --interactive option to provide a shell based ai/ml interaction for querying.
>
> The functionality for static queries (non ai) providing host info, endpoint, and filters -q all works great. I do not want to change any of that. One key reason for adding AI component is to provide a better experience for filtering and display of output. There are thousands of endpoints on fortigate that provide all kinds of different data with different layers and formats (its all returned in json but the relevant data can be in different places and dependent on the type of fuction that api is for, for example but not limited to firewall policies, vs routing info, vs ntp, vs administrators, vs. users, vs antivirus, ips, webfiltering, etc). The goal is for AI to get trained on what is most relevant and by default display the data returned in the most human consumable way possible by default but also to be able to structure filter it and structure it as requested. It will take more training data i'm sure, but right now the app does really respond to filtering, doesn't make any intelligent decisions about what it should display on screen vs. what might not be necessary. it should be able to make a summarized output if requested based on its own decisions ori should be able to request table format, csv, tsv, pdf, html, json, json pretty and specifically tell it what fields i want. If not given specific instructions I would like for it to determine what data is relevant based on training and the best way to show it, if i do give specific instructions about what to fields i want or what format i want it in it should adapt and filter accordingly and provide the requested output. I'd like you to take a comprehensive goal at how to improve the AI part this for both input processing and output processing. I don't want a bunch of static output filters that need to be built per endpoint either, i want it to be dynamic and intelligent like an LLM would do for providing output. We can give it some training or guidelines etc to help it of course. I"d like you to take a deep research look at how to accomplish this form where we are now. (we did start this and you did create a project_plan.md but somehow you ran into an error and it got lost so i guess we have to start from beginning.) Instructions: all temporary files go in /tmp directory. when you execute any code, script, logic on cli run process in bacground and monitor it in case it hangs. update PROJECT_PLAN.md with the plans and what has been completed at each step (including what was done and how) so you can review at a later time if necessary. Also include my instructions in there so i don't need to repeat them.

## 2. Project Goals

Based on the user's instructions, the primary goals are:

- **Enhance Natural Language Input Processing:** Improve the AI's ability to understand user queries, especially regarding filtering and output formatting.
- **Implement Intelligent and Dynamic Output Formatting:** Create a system that can:
    - Automatically select the most relevant data to display.
    - Summarize information.
    - Format output in various formats (table, CSV, TSV, PDF, HTML, JSON, etc.).
    - Adapt to user-specified fields and formats.
- **Avoid Static, Per-Endpoint Solutions:** The solution must be intelligent and generalizable across all FortiGate API endpoints.

## 3. Project Phases

### Phase 1: Code Review and Analysis
- **Status:** Completed
- **Description:** Review the existing codebase to understand the current architecture, AI/ML models, and data processing pipelines. This will help in identifying areas for improvement and formulating a detailed plan.
- **Completed Tasks:**
    - Initial `PROJECT_PLAN.md` created.
    - Reviewed `fgt_api_client.py`, `ml_components/natural_language_interface.py`, `ml_components/enhanced_intent_classifier.py`, `ml_components/ai_formatter.py`, and `ml_demo.py`.
    - Identified that the core issue is the over-reliance on regex for filter/field extraction and static, predefined mappings for output formatting, even with ML models in place for high-level intent classification. The system needs to be more dynamic and data-driven.

### Phase 2: Enhance Input Processing (Natural Language Understanding)
- **Status:** Not Started
- **Description:** Improve the model's ability to understand complex user queries, especially for filtering and field selection. This will involve moving from regex-based extraction to a more robust ML-based approach.
- **Planned Tasks:**
    - **Refine Filter/Field Extraction:** Replace the current regex-based extraction in `enhanced_intent_classifier.py` with a more powerful technique, potentially a Named Entity Recognition (NER) model, to accurately identify filter entities (fields, operators, values) and requested output fields.
    - **Expand Training Data:** Create a new script to generate a comprehensive and robust training dataset. This data will include a wider variety of commands, covering complex filtering, diverse output formats (including PDF), and summarization requests. The new data will be saved in `ml_components/training_data/`.
    - **Retrain Models:** Update the model training process to use the new, richer dataset to train more capable models for intent classification and entity extraction.

### Phase 3: Implement Intelligent Output Formatting
- **Status:** Not Started
- **Description:** Design and implement a new output processing module that is fully dynamic and can handle various formats and intelligently select and summarize data based on the user's query and the data itself.
- **Planned Tasks:**
    - **AI-driven Field Selection:** Enhance the `ai_formatter.py` to use a data-driven approach for selecting the most relevant fields to display. Instead of static mappings, it will analyze the API response and the user's query to determine field importance.
    - **Advanced Summarization:** Implement a more sophisticated summarization capability. This could involve extractive summarization techniques to identify the most significant items and fields from a large data set.
    - **Add PDF Output Format:** Add support for PDF as an output format. This will involve integrating a library like `reportlab` or `fpdf2` and adding it to `requirements.txt`.
    - **Refactor `AIDataFormatter`:** Refactor the `AIDataFormatter` to completely rely on the structured `UserIntent` object from the classifier, removing its internal regex-based parsing.

### Phase 4: Integration and Testing
- **Status:** Not Started
- **Description:** Integrate the new components into the application and conduct thorough testing to ensure everything works as expected.
- **Planned Tasks:**
    - **Update `fgt_api_client.py`:** Modify the main client to fully utilize the enhanced AI components for all AI-powered queries.
    - **Create Comprehensive Tests:** Develop a dedicated test suite (`test_ai_features.py`) to validate the entire AI pipeline, from query understanding to output formatting, across a wide range of scenarios.
    - **Update `ml_demo.py`:** Update the demo script to reflect and showcase the new and improved capabilities.

---
*This document will be updated as the project progresses.*
