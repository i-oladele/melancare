# Evaluation: effb0_sampler

Model: efficientnet_b0, best epoch 1 (validation balanced accuracy 0.775).
Referral thresholds set on validation for 90% sensitivity: malignant >= 0.296, melanoma >= 0.080.

## Internal test (HAM10000, held-out lesions)

1497 images from 1121 lesions. 95% confidence intervals from 1,000 lesion-level bootstrap resamples.

| Metric | Value (95% CI) |
|---|---|
| Accuracy | 0.725 (0.697-0.753) |
| Balanced accuracy | 0.711 (0.654-0.769) |
| Macro F1 | 0.602 (0.544-0.644) |
| Macro AUC | 0.938 (0.926-0.949) |

### Per class

| Class | n | Sensitivity (95% CI) | Specificity | PPV | F1 | AUC (95% CI) |
|---|---|---|---|---|---|---|
| akiec (Actinic keratosis / intraepithelial carcinoma) | 51 | 0.725 (0.597-0.857) | 0.970 | 0.463 | 0.565 | 0.955 (0.924-0.983) |
| bcc (Basal cell carcinoma) | 77 | 0.766 (0.655-0.868) | 0.970 | 0.584 | 0.663 | 0.970 (0.952-0.984) |
| bkl (Benign keratosis-like lesion) | 157 | 0.490 (0.398-0.567) | 0.952 | 0.546 | 0.517 | 0.892 (0.862-0.918) |
| df (Dermatofibroma) | 22 | 0.773 (0.500-1.000) | 0.974 | 0.304 | 0.436 | 0.967 (0.929-0.994) |
| mel (Melanoma) | 168 | 0.690 (0.610-0.773) | 0.867 | 0.396 | 0.503 | 0.874 (0.839-0.903) |
| nv (Melanocytic naevus) | 1000 | 0.762 (0.730-0.793) | 0.928 | 0.955 | 0.848 | 0.929 (0.912-0.945) |
| vasc (Vascular lesion) | 22 | 0.773 (0.562-1.000) | 0.993 | 0.607 | 0.680 | 0.980 (0.953-0.999) |

### Referral decisions

Thresholds were fixed on the validation set to reach the target sensitivity there, then applied unchanged here.

| Task | Positives / negatives | Sensitivity (95% CI) | Specificity (95% CI) | PPV | NPV | AUC (95% CI) |
|---|---|---|---|---|---|---|
| Malignant/premalignant vs benign | 296 / 1201 | 0.909 (0.866-0.945) | 0.673 (0.640-0.705) | 0.406 | 0.968 | 0.892 (0.868-0.915) |
| Melanoma vs rest | 168 / 1329 | 0.935 (0.887-0.973) | 0.603 (0.569-0.637) | 0.230 | 0.986 | 0.874 (0.839-0.903) |

### Subgroups (groups with at least 30 images)

| Attribute | Group | n | Malignant n | Balanced acc. | Malignant sens. | Malignant spec. | Malignant AUC |
|---|---|---|---|---|---|---|---|
| sex | female | 652 | 100 | 0.776 | 0.890 | 0.739 | 0.904 |
| sex | male | 835 | 196 | 0.678 | 0.918 | 0.613 | 0.879 |
| age_band | <30 | 112 | 11 | 0.703 | 1.000 | 0.535 | 0.900 |
| age_band | 30-49 | 485 | 33 | 0.667 | 0.636 | 0.728 | 0.793 |
| age_band | 50-69 | 599 | 104 | 0.711 | 0.942 | 0.701 | 0.908 |
| age_band | 70+ | 296 | 148 | 0.710 | 0.939 | 0.500 | 0.862 |
| localization | abdomen | 155 | 16 | 0.629 | 0.750 | 0.820 | 0.880 |
| localization | back | 345 | 89 | 0.563 | 0.933 | 0.566 | 0.883 |
| localization | chest | 68 | 24 | 0.667 | 0.875 | 0.273 | 0.753 |
| localization | face | 95 | 37 | 0.647 | 0.946 | 0.448 | 0.833 |
| localization | foot | 43 | 1 | 0.357 | 1.000 | 0.643 | 0.976 |
| localization | lower extremity | 291 | 37 | 0.682 | 0.946 | 0.768 | 0.923 |
| localization | scalp | 31 | 14 | 0.544 | 0.786 | 0.471 | 0.752 |
| localization | trunk | 211 | 14 | 0.715 | 0.786 | 0.873 | 0.917 |
| localization | unknown | 42 | 5 | 0.711 | 1.000 | 0.432 | 0.886 |
| localization | upper extremity | 165 | 45 | 0.676 | 0.956 | 0.650 | 0.905 |
| dx_type | consensus | 129 | 0 | 0.703 | n/a | 0.543 | n/a |
| dx_type | follow_up | 554 | 0 | 0.971 | n/a | 0.986 | n/a |
| dx_type | histo | 804 | 296 | 0.643 | 0.909 | 0.366 | 0.788 |
| dataset | rosendahl | 341 | 141 | 0.639 | 0.972 | 0.260 | 0.811 |
| dataset | vidir_modern | 499 | 145 | 0.651 | 0.869 | 0.421 | 0.783 |
| dataset | vidir_molemax | 595 | 5 | 0.682 | 0.200 | 0.983 | 0.849 |
| dataset | vienna_dias | 62 | 5 | 0.852 | 1.000 | 0.474 | 0.842 |

## External test (ISIC 2018 Task 3 test set)

1512 images from 1223 lesions. 95% confidence intervals from 1,000 lesion-level bootstrap resamples.

| Metric | Value (95% CI) |
|---|---|
| Accuracy | 0.718 (0.693-0.744) |
| Balanced accuracy | 0.739 (0.697-0.777) |
| Macro F1 | 0.647 (0.605-0.683) |
| Macro AUC | 0.940 (0.931-0.949) |

### Per class

| Class | n | Sensitivity (95% CI) | Specificity | PPV | F1 | AUC (95% CI) |
|---|---|---|---|---|---|---|
| akiec (Actinic keratosis / intraepithelial carcinoma) | 43 | 0.744 (0.571-0.894) | 0.964 | 0.376 | 0.500 | 0.964 (0.938-0.985) |
| bcc (Basal cell carcinoma) | 93 | 0.796 (0.712-0.876) | 0.977 | 0.692 | 0.740 | 0.980 (0.969-0.988) |
| bkl (Benign keratosis-like lesion) | 217 | 0.562 (0.489-0.634) | 0.942 | 0.619 | 0.589 | 0.888 (0.858-0.915) |
| df (Dermatofibroma) | 44 | 0.841 (0.723-0.946) | 0.974 | 0.493 | 0.622 | 0.974 (0.946-0.992) |
| mel (Melanoma) | 171 | 0.620 (0.525-0.712) | 0.872 | 0.383 | 0.473 | 0.857 (0.824-0.888) |
| nv (Melanocytic naevus) | 909 | 0.754 (0.723-0.786) | 0.929 | 0.941 | 0.837 | 0.930 (0.915-0.943) |
| vasc (Vascular lesion) | 35 | 0.857 (0.722-0.970) | 0.991 | 0.698 | 0.769 | 0.991 (0.978-0.998) |

### Referral decisions

Thresholds were fixed on the validation set to reach the target sensitivity there, then applied unchanged here.

| Task | Positives / negatives | Sensitivity (95% CI) | Specificity (95% CI) | PPV | NPV | AUC (95% CI) |
|---|---|---|---|---|---|---|
| Malignant/premalignant vs benign | 307 / 1205 | 0.912 (0.877-0.945) | 0.676 (0.648-0.705) | 0.418 | 0.968 | 0.896 (0.874-0.916) |
| Melanoma vs rest | 171 / 1341 | 0.936 (0.894-0.973) | 0.551 (0.521-0.581) | 0.210 | 0.985 | 0.857 (0.824-0.888) |

### Subgroups (groups with at least 30 images)

| Attribute | Group | n | Malignant n | Balanced acc. | Malignant sens. | Malignant spec. | Malignant AUC |
|---|---|---|---|---|---|---|---|
| sex | female | 562 | 89 | 0.789 | 0.921 | 0.729 | 0.920 |
| sex | male | 655 | 165 | 0.774 | 0.909 | 0.686 | 0.894 |
| sex | unknown | 294 | 53 | 0.692 | 0.906 | 0.552 | 0.851 |
| age_band | <30 | 117 | 2 | 0.704 | 0.500 | 0.478 | 0.491 |
| age_band | 30-49 | 406 | 30 | 0.870 | 0.867 | 0.798 | 0.920 |
| age_band | 50-69 | 481 | 118 | 0.725 | 0.898 | 0.722 | 0.895 |
| age_band | 70+ | 226 | 106 | 0.786 | 0.953 | 0.567 | 0.882 |
| localization | abdomen | 119 | 5 | 0.872 | 1.000 | 0.807 | 0.974 |
| localization | back | 278 | 66 | 0.759 | 0.924 | 0.542 | 0.817 |
| localization | chest | 47 | 19 | 0.572 | 0.895 | 0.429 | 0.868 |
| localization | face | 94 | 38 | 0.685 | 1.000 | 0.536 | 0.899 |
| localization | foot | 48 | 9 | 0.538 | 0.778 | 0.667 | 0.778 |
| localization | lower extremity | 237 | 33 | 0.750 | 0.939 | 0.819 | 0.956 |
| localization | trunk | 151 | 0 | 0.852 | n/a | 0.921 | n/a |
| localization | unknown | 334 | 70 | 0.705 | 0.914 | 0.534 | 0.854 |
| localization | upper extremity | 139 | 37 | 0.788 | 0.865 | 0.735 | 0.897 |
| dx_type | consensus | 261 | 0 | 0.725 | n/a | 0.632 | n/a |
| dx_type | follow_up | 458 | 0 | 0.983 | n/a | 0.987 | n/a |
| dx_type | histo | 786 | 307 | 0.688 | 0.912 | 0.401 | 0.808 |
| dataset | external | 316 | 68 | 0.702 | 0.912 | 0.540 | 0.851 |
| dataset | rosendahl | 267 | 119 | 0.510 | 0.966 | 0.223 | 0.791 |
| dataset | vidir_modern | 414 | 115 | 0.709 | 0.861 | 0.522 | 0.816 |
| dataset | vidir_molemax | 495 | 1 | 0.747 | 0.000 | 0.982 | 0.929 |
