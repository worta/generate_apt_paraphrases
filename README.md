# Repository
This repository implements the paper "Towards Human Understanding of Paraphrase Types in ChatGPT" (https://arxiv.org/abs/2407.02302).

# Data
The annotated data can be found at [https://github.com/worta/apty/](https://github.com/worta/apty/). The annotation, among others, contains information on whether the application of an atomic paraphrase type was successful,
the reasons for error, and the ranked preferences of humans. For more information, refer to the repository.

# Usage
Edit generate.py, e.g. enter OpenAI key and the experiments you wish to run. Note that each prompt incurs costs at OpenAI. Then start with 
```python
python generate.py
```
To change prompts/base sentences or definitions, change the corresponding files.

# Citation
```bib
@misc{meier2024humanunderstandingparaphrasetypes,
      title={Towards Human Understanding of Paraphrase Types in ChatGPT}, 
      author={Dominik Meier and Jan Philip Wahle and Terry Ruas and Bela Gipp},
      year={2024},
      eprint={2407.02302},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2407.02302}, 
}
```

