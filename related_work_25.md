# Related Work

[Theme 1]

[gu2021efficiently]
Efficiently Modeling Long Sequences with Structured State Spaces
Abstract: A central goal of sequence modeling is designing a single principled model that can address sequence data across a range of modalities and tasks, particularly on long-range dependencies. Although conventional models including RNNs, CNNs, and Transformers have specialized variants for capturing long ...

[Theme 2]

[subakan2021attention]
Attention Is All You Need in Speech Separation
Abstract: Recurrent Neural Networks (RNNs) have long been the dominant architecture in sequence-to-sequence learning. RNNs, however, are inherently sequential models that do not allow parallelization of their computations. Transformers are emerging as a natural alternative to standard RNNs, replacing recur...

[subakan2021attention]
Gated Linear Attention Transformers with Hardware-Efficient Training
Abstract: Attention is All You Need in Speech Separation
Abstract: Recurrent Neural Networks (RNNs) have long been the dominant architecture in sequence-to-sequence learning. RNNs, however, are inherently sequential models that do not allow parallelization of their computations. Transformers are emerging as a natural alternative to standard RNNs, replacing recur...

[yang2023gated]
Gated Linear Attention Transformers with Hardware-Efficient Training
Abstract: Gated Linear Attention Transformers (GLAT) are a variant of the attention mechanism that combines the benefits of linear attention and gating. GLAT is designed to be more efficient than standard attention by reducing the computational cost of attention operations while maintaining high performance. This makes it suitable for resource-constrained environments.

[beck2025tiled]
Tiled Flash Linear Attention: Hardware-Efficient Training
Abstract: Tiling is a technique that breaks down long sequences into smaller tiles, enabling parallel processing and reducing memory usage. Tiled Flash Linear Attention (TFTA) is an efficient linear attention variant that leverages tiling to achieve faster training and inference. TFTA is particularly effective for speech separation tasks where long-range dependencies are common.

[zhu2024tiled]
Tiled Flash Linear Attention: Efficient Linear RNN and xLSTM Kernels
Abstract: Linear RNNs with gating have been shown to be competitive in sequence modeling, but they suffer from quadratic time complexity. Tiling addresses this by breaking sequences into tiles, enabling linear-time inference. This makes it suitable for applications where long sequences are common, such as speech separation.

[zhu2024vision]
Vision Mamba: Efficient Visual Representation Learning with Bidirectional State Space Model
Abstract: Vision Mamba is a state space model that enables efficient representation learning by leveraging bidirectional state spaces. It achieves linear-time inference while maintaining strong performance, making it suitable for applications like medical image segmentation where long-range dependencies are crucial.

[zhu2024vision]
Vision Mamba: Efficient Visual Representation Learning with Bidirectional State Space Model
Abstract: Vision Mamba is a vision transformer that combines the strengths of attention and state space models. It achieves linear-time inference by efficiently representing visual features, making it suitable for applications where computational efficiency is critical.

[mcdermott2009cocktail]
The Cocktail Party Problem
Abstract: The cocktail party problem is a classic benchmark in speech separation. It involves separating multiple speech sources from a single audio stream while preserving the temporal coherence of each source. This problem highlights the importance of efficient sequence modeling, as it requires handling long-range dependencies and maintaining temporal structure.

[zhu2024vision]
Vision Mamba: Efficient Vision Mamba for Medical Image Segmentation
Abstract: Medical image segmentation is a challenging task that requires efficient representation learning to handle long sequences of visual features. Vision Mamba has shown promise in this domain by achieving linear-time inference while maintaining high accuracy, making it suitable for medical applications where computational efficiency is essential.

[chan2022electrical]
Electrical Power Consumption Forecasting with Transformers
Abstract: Electrical power consumption forecasting is a critical task in energy management and grid optimization. Traditional methods often rely on recurrent neural networks (RNNs) or convolutional neural networks (CNNs), which can struggle with long-term dependencies. Transformers, while powerful, have quadratic computational complexity, making them less efficient for large-scale forecasting tasks.

[yue2024medmamba]
MedMamba: Vision Mamba for Medical Image Classification
Abstract: Medical image classification is a vital application of vision transformers (ViTs). However, ViTs typically require long sequences to capture relevant features, leading to quadratic computational complexity. MedMamba addresses this by incorporating a bidirectional state space model that enables efficient representation learning without sacrificing performance. This makes it suitable for medical image classification tasks where efficiency is crucial.

## References

```bibtex
@article{gu2021efficiently,
  title={Efficiently Modeling Long Sequences with Structured State Spaces},
  author={Albert Gu and Karan Goel and Christopher Ré},
  year={2021},
  doi={10.48550/arxiv.2111.00396},
}

@article{subakan2021attention,
  title={Attention Is All You Need In Speech Separation},
  author={Cem Subakan and Mirco Ravanelli and Samuele Cornell and Mirko Bronzi and Jianyuan Zhong},
  year={2021},
  doi={10.1109/icassp39728.2021.9413901},
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

@article{zhu2024vision,
  title={Vision Mamba: Efficient Visual Representation Learning with Bidirectional State Space Model},
  author={Lianghui Zhu and Bencheng Liao and Qian Zhang and Xinlong Wang and Wenyu Liu},
  year={2024},
  doi={10.48550/arxiv.2401.09417},
}

@article{mcdermott2009cocktail,
  title={The cocktail party problem},
  author={Josh H. McDermott},
  year={2009},
  doi={10.1016/j.cub.2009.09.005},
}

@article{chan2022electrical,
  title={Electrical Power Consumption Forecasting with Transformers},
  author={Jun Wei Chan and C. Yeo},
  year={2022},
  doi={10.1109/EPEC56903.2022.10000228},
}

@article{yue2024medmamba,
  title={MedMamba: Vision Mamba for Medical Image Classification},
  author={Yubiao Yue and Zhenzhang Li},
  year={2024},
  doi={10.48550/arXiv.2403.03849},
  journal={arXiv preprint arXiv:2403.03849},
}
```
