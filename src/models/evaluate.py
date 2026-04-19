import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score


def evaluate_model(model, X, y, model_name: str) -> dict:
    """
    Evalue un modele sklearn/LightGBM sur un jeu de donnees.

    Retourne un dict avec :
    - model_name       : nom du modele
    - precision        : precision sur la classe positive
    - recall           : rappel sur la classe positive
    - f1               : F1-score sur la classe positive
    - roc_auc          : AUC-ROC
    - confusion_matrix : matrice de confusion [[TN, FP], [FN, TP]]

    Affiche un rapport formate en console.
    """
    y_pred = model.predict(X)

    # predict_proba disponible sur LR et LightGBM
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X)[:, 1]
    else:
        y_proba = y_pred.astype(float)

    precision = precision_score(y, y_pred, zero_division=0)
    recall = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    auc = roc_auc_score(y, y_proba) if len(np.unique(y)) > 1 else 0.0
    cm = confusion_matrix(y, y_pred).tolist()

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    print(f"  Precision  : {precision:.4f}")
    print(f"  Recall     : {recall:.4f}")
    print(f"  F1         : {f1:.4f}")
    print(f"  AUC-ROC    : {auc:.4f}")
    print(f"  Confusion  : TN={cm[0][0]}  FP={cm[0][1]}  FN={cm[1][0]}  TP={cm[1][1]}")
    print(f"{'='*50}\n")

    return {
        "model_name": model_name,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": auc,
        "confusion_matrix": cm,
    }
