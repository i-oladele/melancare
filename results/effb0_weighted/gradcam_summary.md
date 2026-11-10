# Grad-CAM attention analysis: effb0_weighted

Split: test (1497 images). Heatmaps explain the predicted class.

**Focus ratio** = mean heat inside the lesion / mean heat outside it (1 = no more attention on the lesion than on surrounding skin). **Peak on lesion** = share of images whose hottest point is on the lesion. **Attention not on lesion** = share with focus ratio <= 1. The heatmap share on the lesion depends on lesion size, so read it next to the lesion area.

## Overall

| Group | n | median focus ratio | peak on lesion | attention not on lesion | mean heatmap share on lesion | mean lesion area |
|---|---|---|---|---|---|---|
| all images | 1495 | 13.86 | 0.98 | 0.01 | 0.79 | 0.34 |
| correct | 1155 | 14.27 | 0.99 | 0.01 | 0.81 | 0.34 |
| incorrect | 340 | 12.67 | 0.95 | 0.01 | 0.73 | 0.32 |

## By true diagnosis

| Diagnosis | n | median focus ratio | peak on lesion | attention not on lesion | mean heatmap share on lesion | mean lesion area |
|---|---|---|---|---|---|---|
| akiec | 51 | 5.69 | 0.98 | 0.02 | 0.85 | 0.56 |
| bcc | 77 | 7.03 | 0.99 | 0.01 | 0.73 | 0.37 |
| bkl | 157 | 12.93 | 0.99 | 0.01 | 0.80 | 0.38 |
| df | 22 | 8.47 | 1.00 | 0.00 | 0.73 | 0.35 |
| mel | 167 | 13.51 | 0.99 | 0.00 | 0.84 | 0.40 |
| nv | 999 | 15.53 | 0.98 | 0.01 | 0.79 | 0.31 |
| vasc | 22 | 7.56 | 0.91 | 0.05 | 0.51 | 0.19 |
