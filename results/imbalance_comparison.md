### Internal test (HAM10000)

Overall (95% CI) and referral performance at the validation-set threshold:

| Imbalance method | Balanced accuracy | Macro AUC | Macro F1 | Accuracy | Malignant sens. / spec. | Melanoma sens. / spec. |
|---|---|---|---|---|---|---|
| No correction | 0.710 (0.65-0.77) | 0.967 | 0.690 | 0.835 | 0.895 / 0.818 | 0.935 / 0.735 |
| Oversampling | 0.711 (0.65-0.77) | 0.938 | 0.602 | 0.725 | 0.909 / 0.673 | 0.935 / 0.603 |
| Weighted loss | 0.797 (0.75-0.84) | 0.964 | 0.671 | 0.772 | 0.936 / 0.753 | 0.911 / 0.708 |

Sensitivity per class (arg-max prediction):

| Imbalance method | akiec | bcc | bkl | df | mel | nv | vasc |
|---|---|---|---|---|---|---|---|
| No correction | 0.745 | 0.818 | 0.490 | 0.591 | 0.613 | 0.939 | 0.773 |
| Oversampling | 0.725 | 0.766 | 0.490 | 0.773 | 0.690 | 0.762 | 0.773 |
| Weighted loss | 0.863 | 0.844 | 0.541 | 0.864 | 0.762 | 0.795 | 0.909 |

### External test (ISIC 2018)

Overall (95% CI) and referral performance at the validation-set threshold:

| Imbalance method | Balanced accuracy | Macro AUC | Macro F1 | Accuracy | Malignant sens. / spec. | Melanoma sens. / spec. |
|---|---|---|---|---|---|---|
| No correction | 0.705 (0.66-0.75) | 0.963 | 0.693 | 0.815 | 0.883 / 0.798 | 0.918 / 0.705 |
| Oversampling | 0.739 (0.70-0.78) | 0.940 | 0.647 | 0.718 | 0.912 / 0.676 | 0.936 / 0.551 |
| Weighted loss | 0.751 (0.71-0.79) | 0.956 | 0.666 | 0.752 | 0.919 / 0.740 | 0.924 / 0.680 |

Sensitivity per class (arg-max prediction):

| Imbalance method | akiec | bcc | bkl | df | mel | nv | vasc |
|---|---|---|---|---|---|---|---|
| No correction | 0.744 | 0.731 | 0.613 | 0.795 | 0.544 | 0.936 | 0.571 |
| Oversampling | 0.744 | 0.796 | 0.562 | 0.841 | 0.620 | 0.754 | 0.857 |
| Weighted loss | 0.744 | 0.785 | 0.654 | 0.795 | 0.737 | 0.772 | 0.771 |

