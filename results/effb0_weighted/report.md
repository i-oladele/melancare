# Evaluation: effb0_weighted

Model: efficientnet_b0, best epoch 5 (validation balanced accuracy 0.777).
Referral thresholds set on validation for 90% sensitivity: malignant >= 0.339, melanoma >= 0.112.

## Internal test (HAM10000, held-out lesions)

1497 images from 1121 lesions. 95% confidence intervals from 1,000 lesion-level bootstrap resamples.

| Metric | Value (95% CI) |
|---|---|
| Accuracy | 0.772 (0.747-0.798) |
| Balanced accuracy | 0.797 (0.753-0.837) |
| Macro F1 | 0.671 (0.616-0.713) |
| Macro AUC | 0.964 (0.956-0.971) |

### Per class

| Class | n | Sensitivity (95% CI) | Specificity | PPV | F1 | AUC (95% CI) |
|---|---|---|---|---|---|---|
| akiec (Actinic keratosis / intraepithelial carcinoma) | 51 | 0.863 (0.755-0.956) | 0.967 | 0.478 | 0.615 | 0.980 (0.960-0.993) |
| bcc (Basal cell carcinoma) | 77 | 0.844 (0.761-0.921) | 0.971 | 0.613 | 0.710 | 0.979 (0.968-0.989) |
| bkl (Benign keratosis-like lesion) | 157 | 0.541 (0.458-0.619) | 0.960 | 0.612 | 0.574 | 0.933 (0.910-0.951) |
| df (Dermatofibroma) | 22 | 0.864 (0.630-1.000) | 0.982 | 0.413 | 0.559 | 0.984 (0.963-0.998) |
| mel (Melanoma) | 168 | 0.762 (0.674-0.837) | 0.901 | 0.494 | 0.600 | 0.923 (0.897-0.946) |
| nv (Melanocytic naevus) | 1000 | 0.795 (0.765-0.824) | 0.940 | 0.964 | 0.871 | 0.953 (0.940-0.965) |
| vasc (Vascular lesion) | 22 | 0.909 (0.769-1.000) | 0.993 | 0.667 | 0.769 | 0.998 (0.995-1.000) |

### Referral decisions

Thresholds were fixed on the validation set to reach the target sensitivity there, then applied unchanged here.

| Task | Positives / negatives | Sensitivity (95% CI) | Specificity (95% CI) | PPV | NPV | AUC (95% CI) |
|---|---|---|---|---|---|---|
| Malignant/premalignant vs benign | 296 / 1201 | 0.936 (0.899-0.965) | 0.753 (0.722-0.783) | 0.483 | 0.979 | 0.935 (0.917-0.952) |
| Melanoma vs rest | 168 / 1329 | 0.911 (0.855-0.958) | 0.708 (0.678-0.739) | 0.283 | 0.984 | 0.923 (0.897-0.946) |

### Subgroups (groups with at least 30 images)

| Attribute | Group | n | Malignant n | Balanced acc. | Malignant sens. | Malignant spec. | Malignant AUC |
|---|---|---|---|---|---|---|---|
| sex | female | 652 | 100 | 0.826 | 0.940 | 0.804 | 0.948 |
| sex | male | 835 | 196 | 0.781 | 0.934 | 0.704 | 0.922 |
| age_band | <30 | 112 | 11 | 0.731 | 1.000 | 0.733 | 0.922 |
| age_band | 30-49 | 485 | 33 | 0.771 | 0.697 | 0.810 | 0.856 |
| age_band | 50-69 | 599 | 104 | 0.791 | 0.933 | 0.758 | 0.940 |
| age_band | 70+ | 296 | 148 | 0.787 | 0.986 | 0.568 | 0.924 |
| localization | abdomen | 155 | 16 | 0.806 | 0.812 | 0.885 | 0.942 |
| localization | back | 345 | 89 | 0.738 | 0.944 | 0.652 | 0.910 |
| localization | chest | 68 | 24 | 0.753 | 0.875 | 0.318 | 0.802 |
| localization | face | 95 | 37 | 0.663 | 0.973 | 0.466 | 0.868 |
| localization | foot | 43 | 1 | 0.893 | 1.000 | 0.881 | 0.952 |
| localization | lower extremity | 291 | 37 | 0.718 | 0.946 | 0.831 | 0.970 |
| localization | scalp | 31 | 14 | 0.785 | 0.929 | 0.765 | 0.937 |
| localization | trunk | 211 | 14 | 0.778 | 0.857 | 0.898 | 0.954 |
| localization | unknown | 42 | 5 | 0.785 | 1.000 | 0.703 | 0.962 |
| localization | upper extremity | 165 | 45 | 0.830 | 0.978 | 0.692 | 0.960 |
| dx_type | consensus | 129 | 0 | 0.800 | n/a | 0.729 | n/a |
| dx_type | follow_up | 554 | 0 | 0.978 | n/a | 0.989 | n/a |
| dx_type | histo | 804 | 296 | 0.744 | 0.936 | 0.508 | 0.870 |
| dataset | rosendahl | 341 | 141 | 0.699 | 0.993 | 0.380 | 0.881 |
| dataset | vidir_modern | 499 | 145 | 0.787 | 0.910 | 0.582 | 0.875 |
| dataset | vidir_molemax | 595 | 5 | 0.692 | 0.200 | 0.985 | 0.924 |
| dataset | vienna_dias | 62 | 5 | 0.870 | 0.800 | 0.719 | 0.902 |

## External test (ISIC 2018 Task 3 test set)

1512 images from 1223 lesions. 95% confidence intervals from 1,000 lesion-level bootstrap resamples.

| Metric | Value (95% CI) |
|---|---|
| Accuracy | 0.752 (0.728-0.776) |
| Balanced accuracy | 0.751 (0.707-0.790) |
| Macro F1 | 0.666 (0.622-0.705) |
| Macro AUC | 0.956 (0.947-0.964) |

### Per class

| Class | n | Sensitivity (95% CI) | Specificity | PPV | F1 | AUC (95% CI) |
|---|---|---|---|---|---|---|
| akiec (Actinic keratosis / intraepithelial carcinoma) | 43 | 0.744 (0.571-0.886) | 0.959 | 0.348 | 0.474 | 0.976 (0.961-0.989) |
| bcc (Basal cell carcinoma) | 93 | 0.785 (0.695-0.867) | 0.973 | 0.652 | 0.712 | 0.972 (0.955-0.984) |
| bkl (Benign keratosis-like lesion) | 217 | 0.654 (0.580-0.728) | 0.953 | 0.700 | 0.676 | 0.926 (0.903-0.947) |
| df (Dermatofibroma) | 44 | 0.795 (0.641-0.914) | 0.980 | 0.538 | 0.642 | 0.983 (0.971-0.993) |
| mel (Melanoma) | 171 | 0.737 (0.650-0.811) | 0.894 | 0.470 | 0.574 | 0.907 (0.874-0.931) |
| nv (Melanocytic naevus) | 909 | 0.772 (0.742-0.805) | 0.949 | 0.958 | 0.855 | 0.953 (0.940-0.964) |
| vasc (Vascular lesion) | 35 | 0.771 (0.600-0.898) | 0.992 | 0.692 | 0.730 | 0.977 (0.946-0.998) |

### Referral decisions

Thresholds were fixed on the validation set to reach the target sensitivity there, then applied unchanged here.

| Task | Positives / negatives | Sensitivity (95% CI) | Specificity (95% CI) | PPV | NPV | AUC (95% CI) |
|---|---|---|---|---|---|---|
| Malignant/premalignant vs benign | 307 / 1205 | 0.919 (0.877-0.952) | 0.740 (0.711-0.768) | 0.474 | 0.973 | 0.921 (0.899-0.939) |
| Melanoma vs rest | 171 / 1341 | 0.924 (0.877-0.964) | 0.680 (0.652-0.711) | 0.269 | 0.986 | 0.907 (0.874-0.931) |

### Subgroups (groups with at least 30 images)

| Attribute | Group | n | Malignant n | Balanced acc. | Malignant sens. | Malignant spec. | Malignant AUC |
|---|---|---|---|---|---|---|---|
| sex | female | 562 | 89 | 0.767 | 0.910 | 0.772 | 0.933 |
| sex | male | 655 | 165 | 0.747 | 0.921 | 0.743 | 0.912 |
| sex | unknown | 294 | 53 | 0.712 | 0.925 | 0.672 | 0.916 |
| age_band | <30 | 117 | 2 | 0.595 | 0.500 | 0.661 | 0.683 |
| age_band | 30-49 | 406 | 30 | 0.749 | 0.900 | 0.827 | 0.958 |
| age_band | 50-69 | 481 | 118 | 0.747 | 0.898 | 0.749 | 0.905 |
| age_band | 70+ | 226 | 106 | 0.819 | 0.953 | 0.642 | 0.909 |
| localization | abdomen | 119 | 5 | 0.841 | 1.000 | 0.842 | 0.968 |
| localization | back | 278 | 66 | 0.837 | 0.955 | 0.590 | 0.882 |
| localization | chest | 47 | 19 | 0.601 | 0.895 | 0.464 | 0.842 |
| localization | face | 94 | 38 | 0.670 | 0.947 | 0.536 | 0.886 |
| localization | foot | 48 | 9 | 0.714 | 0.556 | 0.769 | 0.729 |
| localization | lower extremity | 237 | 33 | 0.733 | 0.939 | 0.863 | 0.950 |
| localization | trunk | 151 | 0 | 0.888 | n/a | 0.960 | n/a |
| localization | unknown | 334 | 70 | 0.710 | 0.914 | 0.659 | 0.910 |
| localization | upper extremity | 139 | 37 | 0.710 | 0.892 | 0.765 | 0.928 |
| dx_type | consensus | 261 | 0 | 0.742 | n/a | 0.690 | n/a |
| dx_type | follow_up | 458 | 0 | 0.985 | n/a | 0.993 | n/a |
| dx_type | histo | 786 | 307 | 0.691 | 0.919 | 0.524 | 0.856 |
| dataset | external | 316 | 68 | 0.712 | 0.912 | 0.673 | 0.910 |
| dataset | rosendahl | 267 | 119 | 0.551 | 0.966 | 0.365 | 0.843 |
| dataset | vidir_modern | 414 | 115 | 0.699 | 0.878 | 0.572 | 0.844 |
| dataset | vidir_molemax | 495 | 1 | 0.672 | 0.000 | 0.988 | 0.743 |
