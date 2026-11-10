# Evaluation: effb0_none

Model: efficientnet_b0, best epoch 5 (validation balanced accuracy 0.745).
Referral thresholds set on validation for 90% sensitivity: malignant >= 0.170, melanoma >= 0.038.

## Internal test (HAM10000, held-out lesions)

1497 images from 1121 lesions. 95% confidence intervals from 1,000 lesion-level bootstrap resamples.

| Metric | Value (95% CI) |
|---|---|
| Accuracy | 0.835 (0.813-0.857) |
| Balanced accuracy | 0.710 (0.647-0.767) |
| Macro F1 | 0.690 (0.634-0.734) |
| Macro AUC | 0.967 (0.960-0.974) |

### Per class

| Class | n | Sensitivity (95% CI) | Specificity | PPV | F1 | AUC (95% CI) |
|---|---|---|---|---|---|---|
| akiec (Actinic keratosis / intraepithelial carcinoma) | 51 | 0.745 (0.595-0.891) | 0.978 | 0.543 | 0.628 | 0.981 (0.968-0.992) |
| bcc (Basal cell carcinoma) | 77 | 0.818 (0.714-0.917) | 0.973 | 0.624 | 0.708 | 0.981 (0.971-0.990) |
| bkl (Benign keratosis-like lesion) | 157 | 0.490 (0.392-0.575) | 0.980 | 0.740 | 0.590 | 0.946 (0.926-0.963) |
| df (Dermatofibroma) | 22 | 0.591 (0.333-0.842) | 0.985 | 0.371 | 0.456 | 0.978 (0.962-0.991) |
| mel (Melanoma) | 168 | 0.613 (0.518-0.712) | 0.963 | 0.678 | 0.644 | 0.930 (0.907-0.952) |
| nv (Melanocytic naevus) | 1000 | 0.939 (0.921-0.956) | 0.841 | 0.922 | 0.931 | 0.959 (0.946-0.970) |
| vasc (Vascular lesion) | 22 | 0.773 (0.500-1.000) | 1.000 | 1.000 | 0.872 | 0.996 (0.988-1.000) |

### Referral decisions

Thresholds were fixed on the validation set to reach the target sensitivity there, then applied unchanged here.

| Task | Positives / negatives | Sensitivity (95% CI) | Specificity (95% CI) | PPV | NPV | AUC (95% CI) |
|---|---|---|---|---|---|---|
| Malignant/premalignant vs benign | 296 / 1201 | 0.895 (0.850-0.936) | 0.818 (0.790-0.842) | 0.548 | 0.969 | 0.943 (0.926-0.958) |
| Melanoma vs rest | 168 / 1329 | 0.935 (0.895-0.969) | 0.735 (0.704-0.766) | 0.308 | 0.989 | 0.930 (0.907-0.952) |

### Subgroups (groups with at least 30 images)

| Attribute | Group | n | Malignant n | Balanced acc. | Malignant sens. | Malignant spec. | Malignant AUC |
|---|---|---|---|---|---|---|---|
| sex | female | 652 | 100 | 0.792 | 0.900 | 0.873 | 0.956 |
| sex | male | 835 | 196 | 0.671 | 0.893 | 0.767 | 0.930 |
| age_band | <30 | 112 | 11 | 0.636 | 0.727 | 0.851 | 0.836 |
| age_band | 30-49 | 485 | 33 | 0.626 | 0.576 | 0.876 | 0.897 |
| age_band | 50-69 | 599 | 104 | 0.680 | 0.923 | 0.806 | 0.949 |
| age_band | 70+ | 296 | 148 | 0.642 | 0.959 | 0.649 | 0.928 |
| localization | abdomen | 155 | 16 | 0.620 | 0.812 | 0.928 | 0.957 |
| localization | back | 345 | 89 | 0.680 | 0.888 | 0.773 | 0.931 |
| localization | chest | 68 | 24 | 0.864 | 0.875 | 0.614 | 0.876 |
| localization | face | 95 | 37 | 0.731 | 0.973 | 0.448 | 0.895 |
| localization | foot | 43 | 1 | 0.964 | 1.000 | 0.976 | 1.000 |
| localization | lower extremity | 291 | 37 | 0.587 | 0.946 | 0.831 | 0.960 |
| localization | scalp | 31 | 14 | 0.765 | 1.000 | 0.882 | 0.992 |
| localization | trunk | 211 | 14 | 0.825 | 0.643 | 0.964 | 0.969 |
| localization | unknown | 42 | 5 | 0.625 | 1.000 | 0.838 | 0.984 |
| localization | upper extremity | 165 | 45 | 0.768 | 0.911 | 0.750 | 0.948 |
| dx_type | consensus | 129 | 0 | 0.814 | n/a | 0.860 | n/a |
| dx_type | follow_up | 554 | 0 | 0.995 | n/a | 0.993 | n/a |
| dx_type | histo | 804 | 296 | 0.660 | 0.895 | 0.626 | 0.884 |
| dataset | rosendahl | 341 | 141 | 0.677 | 0.943 | 0.520 | 0.880 |
| dataset | vidir_modern | 499 | 145 | 0.645 | 0.876 | 0.703 | 0.898 |
| dataset | vidir_molemax | 595 | 5 | 0.722 | 0.200 | 0.992 | 0.962 |
| dataset | vienna_dias | 62 | 5 | 0.926 | 0.800 | 0.772 | 0.954 |

## External test (ISIC 2018 Task 3 test set)

1512 images from 1223 lesions. 95% confidence intervals from 1,000 lesion-level bootstrap resamples.

| Metric | Value (95% CI) |
|---|---|
| Accuracy | 0.815 (0.791-0.838) |
| Balanced accuracy | 0.705 (0.660-0.748) |
| Macro F1 | 0.693 (0.646-0.735) |
| Macro AUC | 0.963 (0.955-0.971) |

### Per class

| Class | n | Sensitivity (95% CI) | Specificity | PPV | F1 | AUC (95% CI) |
|---|---|---|---|---|---|---|
| akiec (Actinic keratosis / intraepithelial carcinoma) | 43 | 0.744 (0.583-0.879) | 0.980 | 0.516 | 0.610 | 0.977 (0.957-0.992) |
| bcc (Basal cell carcinoma) | 93 | 0.731 (0.631-0.821) | 0.974 | 0.648 | 0.687 | 0.973 (0.960-0.984) |
| bkl (Benign keratosis-like lesion) | 217 | 0.613 (0.538-0.691) | 0.977 | 0.816 | 0.700 | 0.942 (0.921-0.960) |
| df (Dermatofibroma) | 44 | 0.795 (0.657-0.917) | 0.988 | 0.660 | 0.722 | 0.985 (0.970-0.995) |
| mel (Melanoma) | 171 | 0.544 (0.446-0.636) | 0.955 | 0.608 | 0.574 | 0.910 (0.876-0.938) |
| nv (Melanocytic naevus) | 909 | 0.936 (0.916-0.954) | 0.837 | 0.897 | 0.916 | 0.962 (0.950-0.972) |
| vasc (Vascular lesion) | 35 | 0.571 (0.394-0.750) | 0.995 | 0.741 | 0.645 | 0.993 (0.988-0.997) |

### Referral decisions

Thresholds were fixed on the validation set to reach the target sensitivity there, then applied unchanged here.

| Task | Positives / negatives | Sensitivity (95% CI) | Specificity (95% CI) | PPV | NPV | AUC (95% CI) |
|---|---|---|---|---|---|---|
| Malignant/premalignant vs benign | 307 / 1205 | 0.883 (0.833-0.927) | 0.798 (0.770-0.824) | 0.526 | 0.964 | 0.924 (0.901-0.945) |
| Melanoma vs rest | 171 / 1341 | 0.918 (0.867-0.962) | 0.705 (0.679-0.733) | 0.284 | 0.985 | 0.910 (0.876-0.938) |

### Subgroups (groups with at least 30 images)

| Attribute | Group | n | Malignant n | Balanced acc. | Malignant sens. | Malignant spec. | Malignant AUC |
|---|---|---|---|---|---|---|---|
| sex | female | 562 | 89 | 0.780 | 0.888 | 0.848 | 0.932 |
| sex | male | 655 | 165 | 0.654 | 0.873 | 0.784 | 0.921 |
| sex | unknown | 294 | 53 | 0.684 | 0.906 | 0.730 | 0.926 |
| age_band | <30 | 117 | 2 | 0.472 | 0.000 | 0.704 | 0.343 |
| age_band | 30-49 | 406 | 30 | 0.664 | 0.900 | 0.888 | 0.965 |
| age_band | 50-69 | 481 | 118 | 0.747 | 0.856 | 0.818 | 0.909 |
| age_band | 70+ | 226 | 106 | 0.811 | 0.915 | 0.675 | 0.916 |
| localization | abdomen | 119 | 5 | 0.739 | 0.600 | 0.912 | 0.914 |
| localization | back | 278 | 66 | 0.702 | 0.864 | 0.726 | 0.884 |
| localization | chest | 47 | 19 | 0.707 | 0.842 | 0.643 | 0.848 |
| localization | face | 94 | 38 | 0.724 | 0.974 | 0.571 | 0.927 |
| localization | foot | 48 | 9 | 0.474 | 0.333 | 0.872 | 0.681 |
| localization | lower extremity | 237 | 33 | 0.738 | 0.879 | 0.897 | 0.962 |
| localization | trunk | 151 | 0 | 0.833 | n/a | 0.967 | n/a |
| localization | unknown | 334 | 70 | 0.687 | 0.914 | 0.716 | 0.927 |
| localization | upper extremity | 139 | 37 | 0.513 | 0.892 | 0.775 | 0.910 |
| dx_type | consensus | 261 | 0 | 0.762 | n/a | 0.766 | n/a |
| dx_type | follow_up | 458 | 0 | 0.998 | n/a | 0.993 | n/a |
| dx_type | histo | 786 | 307 | 0.660 | 0.883 | 0.630 | 0.862 |
| dataset | external | 316 | 68 | 0.691 | 0.912 | 0.718 | 0.926 |
| dataset | rosendahl | 267 | 119 | 0.588 | 0.924 | 0.459 | 0.852 |
| dataset | vidir_modern | 414 | 115 | 0.651 | 0.826 | 0.719 | 0.846 |
| dataset | vidir_molemax | 495 | 1 | 0.680 | 0.000 | 0.986 | 0.960 |
