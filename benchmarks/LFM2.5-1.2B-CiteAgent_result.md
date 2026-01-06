# Related Work

[Theme 1]
[subakan2020attention] Attention Is All You Need In Speech Separation
Abstract: Recurrent Neural Networks (RNNs) have long been the dominant architecture in sequence-to-sequence learning. RNNs, however, are inherently sequential models that do not allow parallelization of their computations. Transformers are emerging as a natural alternative to standard RNNs, replacing recur...

[subakan2021attention] Attention Is All You Need In Speech Separation
Abstract: Recurrent Neural Networks (RNNs) have long been the dominant architecture in sequence-to-sequence learning. RNNs, however, are inherently sequential models that do not allow parallelization of their computations. Transformers are emerging as a natural alternative to standard RNNs, replacing recur...

[jiang2024dualpath] Dual-path Mamba: Short and Long-term Bidirectional Selective Structured State Space Models for Speech Separation
Abstract: (No Abstract)

[li2025spmamba] SPMamba: Leveraging Long-Sequence Modeling with State Space Models for Speech Separation
Abstract: (No Abstract)

[li2024spmamba] SPMamba: State-space model is all you need in speech separation
Abstract: Existing CNN-based speech separation models face local receptive field limitations and cannot effectively capture long time dependencies. Although LSTM and Transformer-based speech separation models can avoid this problem, their high complexity makes them face the challenge of computational resource...

[theme 2]
[xu2022dualpath] Dual-path Attention is All You Need for Audio-Visual Speech Extraction
Abstract: (No Abstract)

[li2024spmamba] SPMamba: State-space model is all you need in speech separation
Abstract: (No Abstract)

[theme 3]
[dai2019transformerxl] Transformer-XL: Attentive Language Models beyond a Fixed-Length Context
Abstract: Transformers have a potential of learning long-term dependency, but are limited by a fixed-length context in the setting of language modeling. We propose a novel neural architecture Transformer-XL that enables learning dependency beyond a fixed length without disrupting temporal coherence. It consists of two parts: a linear layer that maps the input sequence to a fixed-size vector and a gated attention mechanism that allows for flexible, non-linear attention over the entire sequence. This design enables the model to capture long-range dependencies while maintaining computational efficiency.

[gu2021efficiently] Efficiently Modeling Long Sequences with Structured State Spaces
Abstract: A central goal of sequence modeling is designing a single principled model that can address sequence data across a range of modalities and tasks, particularly on long-range dependencies. Although conventional models including RNNs, CNNs, and Transformers have specialized variants for capturing long ...

[yang2023gated] Gated Linear Attention Transformers with Hardware-Efficient Training
Abstract: (No Abstract)

[beck2025tiled] Tiled Flash Linear Attention: More Efficient Linear RNN and xLSTM Kernels
Abstract: Linear RNNs with gating recently demonstrated competitive performance compared to Transformers in language modeling. However, their linear compute scaling in sequence length offers theoretical runtime advantages over Transformers. To realize these benefits in practice, we propose a hardware-optimized variant of the Tiled Flash Linear Attention mechanism that reduces memory access and improves inference speed while maintaining accuracy.

## References

```bibtex
@article{subakan2020attention,
  title={Attention Is All You Need In Speech Separation},
  author={Cem Subakan and M. Ravanelli and Samuele Cornell and Mirko Bronzi and Jianyuan Zhong},
  year={2020},
  doi={10.1109/ICASSP39728.2021.9413901},
  journal={arXiv preprint arXiv:2010.13154},
}

@article{subakan2021attention,
  title={Attention Is All You Need In Speech Separation},
  author={Cem Subakan and Mirco Ravanelli and Samuele Cornell and Mirko Bronzi and Jianyuan Zhong},
  year={2021},
  doi={10.1109/icassp39728.2021.9413901},
}

@article{jiang2024dualpath,
  title={Dual-path Mamba: Short and Long-term Bidirectional Selective Structured State Space Models for Speech Separation},
  author={Xilin Jiang and Cong Han and N. Mesgarani},
  year={2024},
  doi={10.1109/ICASSP49660.2025.10888514},
  journal={arXiv preprint arXiv:2403.18257},
}

@article{li2025spmamba,
  title={SPMamba: Leveraging Long-Sequence Modeling with State Space Models for Speech Separation},
  author={Kai Li and Guo Chen and Run Yang and Xiaolin Hu},
  year={2025},
  doi={10.1109/ICME59968.2025.11209217},
}

@article{li2024spmamba,
  title={SPMamba: State-space model is all you need in speech separation},
  author={Kai Li and Chen Guo},
  year={2024},
  doi={10.48550/arxiv.2404.02063},
}

@article{xu2022dualpath,
  title={Dual-path Attention is All You Need for Audio-Visual Speech Extraction},
  author={Zhongweiyang Xu and Xulin Fan and M. Hasegawa-Johnson},
  year={2022},
  doi={10.48550/arXiv.2207.04213},
}

@article{dai2019transformerxl,
  title={Transformer-XL: Attentive Language Models beyond a Fixed-Length Context},
  author={Zihang Dai and Zhilin Yang and Yiming Yang and Jaime Carbonell and Quoc V. Le},
  year={2019},
  doi={10.18653/v1/p19-1285},
}

@article{gu2021efficiently,
  title={Efficiently Modeling Long Sequences with Structured State Spaces},
  author={Albert Gu and Karan Goel and Christopher Ré},
  year={2021},
  doi={10.48550/arxiv.2111.00396},
}

@article{yang2023gated,
  title={Gated Linear Attention Transformers with Hardware-Efficient Training},
  author={Songlin Yang and Bailin Wang and Yikang Shen and Rameswar Panda and Yoon Kim},
  year={2023},
  doi={10.48550/arXiv.2312.06635},
  journal={arXiv preprint arXiv:2312.06635},
}

@article{beck2025tiled,
  title={Tiled Flash Linear Attention: More Efficient Linear RNN and xLSTM Kernels},
  author={Maximilian Beck and Korbinian Pöppel and Phillip Lippe and Sepp Hochreiter},
  year={2025},
  doi={10.48550/arXiv.2503.14376},
  journal={arXiv preprint arXiv:2503.14376},
}
```
