import fiona
import rasterio
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix
import argparse

def calculate_accuracy_metrics(conf_matrix):
    """
    Function to calculate accuracy metrics from a confusion matrix.
    """
    overall_accuracy = np.sum(np.diag(conf_matrix)) / np.sum(conf_matrix)
    producer_accuracy = np.diag(conf_matrix) / np.sum(conf_matrix, axis=1)
    user_accuracy = np.diag(conf_matrix) / np.sum(conf_matrix, axis=0)
    total = np.sum(conf_matrix)
    p0 = np.sum(np.diag(conf_matrix)) / total
    pe = np.sum(np.sum(conf_matrix, axis=0) * np.sum(conf_matrix, axis=1)) / (total**2)
    kappa = (p0 - pe) / (1 - pe)
    
    return overall_accuracy, producer_accuracy, user_accuracy, kappa
	
def validate_lulc(shapefile_path, geotiff_path, lulc_field_name):
    """
    Function to validate the LULC classification by comparing predicted LULC values from the 
    GeoTIFF with true LULC values from the shapefile and computing accuracy metrics.
    """
    with fiona.open(shapefile_path, 'r') as shapefile:
        with rasterio.open(geotiff_path) as src:
            lulc_array = src.read(1)
            transform = src.transform
            lulc_values_pred = []
            lulc_values_true = []
            
            for feature in shapefile:
                x, y = feature['geometry']['coordinates']
                col, row = ~transform * (x, y)
                col, row = int(col), int(row)
                lulc_pred = lulc_array[row, col]
                lulc_true = feature['properties'][lulc_field_name]
                lulc_values_pred.append(lulc_pred)
                lulc_values_true.append(lulc_true)
    
    cm = confusion_matrix(lulc_values_true, lulc_values_pred)
    overall_accuracy, producer_accuracy, user_accuracy, kappa = calculate_accuracy_metrics(cm)
    
    accuracy_metrics = {
        "Confusion Matrix": cm,
        "Overall Accuracy": overall_accuracy,
        "Producer Accuracy": producer_accuracy,
        "User Accuracy": user_accuracy,
        "Kappa": kappa
    }
    
    return accuracy_metrics


def load_labels(label_file):
    """
    Function to load the LULC codes and corresponding labels from a CSV file.
    """
    label_df = pd.read_csv(label_file)
    label_dict = dict(zip(label_df['LULC_Code'], label_df['Label']))
    return label_dict


def plot_confusion_matrix_heatmap(conf_matrix, label_dict, fig_path):
    """
    Function to plot the heatmap of a confusion matrix with human-readable labels.
    """
    labels = [label_dict.get(i, str(i)) for i in range(conf_matrix.shape[0])]
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='g', cmap='Blues', cbar=False, 
                xticklabels=labels, yticklabels=labels)
    
    plt.title('Confusion Matrix Heatmap')
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')
    plt.tight_layout()
    plt.savefig(fig_path)
    plt.show()
	
def save_class_accuracies_to_csv(producer_accuracy, user_accuracy, label_dict, output_csv_path):
    """
    Function to save the Producer and User Accuracy for each LULC class with labels to a CSV file.
    """
    data = []
    
    for code, label in label_dict.items():
        if code < len(producer_accuracy):  # Ensure class code exists in the matrix
            data.append({
                "Code": code,
                "Label": label,
                "Producer Accuracy": producer_accuracy[code],
                "User Accuracy": user_accuracy[code]
            })
    
    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False)
    print(f"Class accuracies saved to {output_csv_path}")


def main(args):
    # Load the label dictionary from the CSV file
    label_dict = load_labels(args.label_file)
    
    # Validate LULC classification and calculate accuracy metrics
    accuracy_metrics = validate_lulc(args.shapefile, args.geotiff, args.lulc_field)

    # Print the results if requested
    if args.print_accuracies:
        print("Confusion Matrix:")
        print(accuracy_metrics["Confusion Matrix"])
        print(f"Overall Accuracy: {accuracy_metrics['Overall Accuracy']:.4f}")
        print(f"Producer Accuracy: {accuracy_metrics['Producer Accuracy']}")
        print(f"User Accuracy: {accuracy_metrics['User Accuracy']}")
        print(f"Kappa Statistic: {accuracy_metrics['Kappa']:.4f}")
    
    # Save class accuracies to CSV if requested
    if args.save_accuracies_csv:
        save_class_accuracies_to_csv(accuracy_metrics["Producer Accuracy"], 
                                     accuracy_metrics["User Accuracy"], 
                                     label_dict, args.output_csv_path)

    # Plot Confusion Matrix Heatmap if requested
    if args.plot_heatmap:
        fig_path = args.output_fig_path
        plot_confusion_matrix_heatmap(accuracy_metrics["Confusion Matrix"], label_dict, fig_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LULC validation script")
    
    parser.add_argument('shapefile', type=str, help="Path to the shapefile with validation points")
    parser.add_argument('geotiff', type=str, help="Path to the GeoTIFF with LULC predictions")
    parser.add_argument('lulc_field', type=str, help="The attribute field in the shapefile containing LULC values")
    parser.add_argument('label_file', type=str, help="Path to the CSV file with LULC codes and labels")
    parser.add_argument('--plot_heatmap', action='store_true', help="Plot confusion matrix heatmap")
    parser.add_argument('--print_accuracies', action='store_true', help="Print accuracy metrics")
    parser.add_argument('--save_accuracies_csv', action='store_true', help="Save class accuracies to a CSV file")
    parser.add_argument('--output_fig_path', type=str, default='confusion_matrix_heatmap.png', help="Output path for heatmap figure")
    parser.add_argument('--output_csv_path', type=str, default='producer_user_accuracies.csv', help="Path to save class accuracies as CSV file")
    
    args = parser.parse_args()

    main(args)
