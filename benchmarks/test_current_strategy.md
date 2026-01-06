# Related Work

[Theme 1]
[dai2019transformerxl] Transformer-XL: Attentive Language Models beyond a Fixed-Length Context
Abstract: Transformers have a potential of learning longer-term dependency, but are limited by a fixed-length context in the setting of language modeling. We propose a novel neural architecture Transformer-XL that enables learning dependency beyond a fixed length without disrupting temporal coherence. It cons...

[lu2023structured] Structured State Space Models for In-Context Reinforcement Learning
Abstract: Structured state space sequence (S4) models have recently achieved state-of-the-art performance on long-range sequence modeling tasks. These models also have fast inference speeds and parallelisable training, making them potentially useful in many reinforcement learning settings. We propose a modifi...

[qiu2021dbtmpe] DBTMPE: Deep Bidirectional Transformers-Based Masked Predictive Encoder Approach for Music Genre Classification
Abstract: Music is a type of time-series data. As the size of the data increases, it is a challenge to build robust music genre classification systems from massive amounts of music data. Robust systems require large amounts of labeled music data, which necessitates time- and labor-intensive data-labeling effo...

[Theme 2]
[chen2024video] Video Mamba Suite: State Space Model as a Versatile Alternative for Video Understanding
Abstract: Understanding videos is one of the fundamental directions in computer vision research, with extensive efforts dedicated to exploring various architectures such as RNN, 3D CNN, and Transformers. The newly proposed architecture of state space model, e.g., Mamba, shows promising traits to extend its su...

[zhang2024survey] A Survey on Visual Mamba
Abstract: State space models (SSM) with selection mechanisms and hardware-aware architectures, namely Mamba, have recently shown significant potential in long-sequence modeling. Since the complexity of transformers’ self-attention mechanism is quadratic with image size, as well as increasing computational dem...

[Theme 3]
[subakan2020attention] Attention Is All You Need In Speech Separation
Abstract: Recurrent Neural Networks (RNNs) have long been the dominant architecture in sequence-to-sequence learning. RNNs, however, are inherently sequential models that do not allow parallelization of their computations. Transformers are emerging as a natural alternative to standard RNNs, replacing recurren...

[hashmi2024multiclass] Multi-class hate speech detection in the Norwegian language using FAST-RNN and multilingual fine-tuned transformers
Abstract: The growth of social networks has provided a platform for individuals with prejudiced views, allowing them to spread hate speech and target others based on their gender, ethnicity, religion, or sexual orientation. While positive interactions within diverse communities can considerably enhance confid...

[krishna2019eeg] EEG based Continuous Speech Recognition using Transformers
Abstract: In this paper we investigate continuous speech recognition using electroencephalography (EEG) features using recently introduced end-to-end transformer based automatic speech recognition (ASR) model. Our results demonstrate that transformer based model demonstrate faster training compared to recurre...

### Summary:
The references can be grouped into three themes based on the User Idea of making RNN models like LSTM and GRU faster than Transformers:

**Theme 1: State Space Models for Sequence Modeling**
- [dai2019transformerxl]: Transformer-XL
- [lu2023structured]: Structured State Space Models
- [qiu2021dbtmpe]: DBTMPE
- [zhang2024survey]: A Survey on Visual Mamba

**Theme 2: Efficient Sequence Modeling**
- [hashmi2024multiclass]: Multi-class hate speech detection using Mamba
- [krishna2019eeg]: EEG based Continuous Speech Recognition using Transformers
- [subakan2020attention]: Attention Is All You Need In Speech Separation

**Theme 3: Alternative Architectures for Sequence Tasks**
- [chen2024video]: Video Mamba Suite
- [zhang2024survey]: A Survey on Visual Mamba
- [hashmi2024multiclass]: Multi-class hate speech detection using FAST-RNN and multilingual fine-tuned transformers

These models offer alternative approaches to sequence modeling, potentially enabling faster inference compared to Transformers. State space models (SSMs) like Mamba show promise in handling long sequences efficiently, while efficient attention-based models may reduce computational complexity. The focus is on leveraging architectural innovations to achieve performance comparable to Transformers with lower resource demands.

The references highlight the versatility of SSMs and attention mechanisms in various domains, suggesting that these architectures can be adapted for faster sequence modeling tasks. The emphasis is on reducing computational overhead without sacrificing

## References

```bibtex
@article{dai2019transformerxl,
  title={Transformer-XL: Attentive Language Models beyond a Fixed-Length Context},
  author={Zihang Dai and Zhilin Yang and Yiming Yang and Jaime Carbonell and Quoc V. Le},
  year={2019},
  doi={10.18653/v1/p19-1285},
}

@article{lu2023structured,
  title={Structured State Space Models for In-Context Reinforcement Learning},
  author={Chris Xiaoxuan Lu and Yannick Schroecker and Albert Gu and Emilio Parisotto and J. Foerster and Satinder Singh and Feryal M. P. Behbahani},
  year={2023},
  doi={10.48550/arXiv.2303.03982},
  journal={arXiv preprint arXiv:2303.03982},
}

@article{qiu2021dbtmpe,
  title={DBTMPE: Deep Bidirectional Transformers-Based Masked Predictive Encoder Approach for Music Genre Classification},
  author={Lvyang Qiu and Shuyu Li and Yunsick Sung},
  year={2021},
  doi={10.3390/MATH9050530},
}

@article{chen2024video,
  title={Video Mamba Suite: State Space Model as a Versatile Alternative for Video Understanding},
  author={Guo Chen and Yifei Huang and Jilan Xu and Baoqi Pei and Zhe Chen and Zhiqi Li and Jiahao Wang and Kunchang Li and Tong Lu and Limin Wang},
  year={2024},
  doi={10.48550/arXiv.2403.09626},
  journal={arXiv preprint arXiv:2403.09626},
}

@article{zhang2024survey,
  title={A Survey on Visual Mamba},
  author={Hanwei Zhang and Ying Zhu and Dan Wang and Lijun Zhang and Tianxiang Chen},
  year={2024},
  doi={10.3390/app14135683},
}

@article{subakan2020attention,
  title={Attention Is All You Need In Speech Separation},
  author={Cem Subakan and M. Ravanelli and Samuele Cornell and Mirko Bronzi and Jianyuan Zhong},
  year={2020},
  doi={10.1109/ICASSP39728.2021.9413901},
  journal={arXiv preprint arXiv:2010.13154},
}

@article{hashmi2024multiclass,
  title={Multi-class hate speech detection in the Norwegian language using FAST-RNN and multilingual fine-tuned transformers},
  author={Ehtesham Hashmi and Sule YAYILGAN YILDIRIM},
  year={2024},
  doi={10.1007/s40747-024-01392-5},
}

@article{krishna2019eeg,
  title={EEG based Continuous Speech Recognition using Transformers},
  author={G. Krishna and Co Tran and Mason Carnahan and A. Tewfik},
  year={2019},
  journal={arXiv preprint arXiv:2001.00501},
}
```
