def get_dashboard_css():
    """Return the CSS styles for the dashboard."""
    return """
        <style>
        .property-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .property-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .property-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .property-title {
            font-size: 1.2em;
            font-weight: bold;
            margin: 10px 0;
            color: #1f1f1f;
        }
        .property-price {
            font-size: 1.1em;
            color: #2e7d32;
            font-weight: bold;
            margin: 5px 0;
        }
        .property-details {
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }
        .criteria-tag {
            display: inline-block;
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 4px;
            margin: 2px;
            font-size: 0.8em;
        }
        .view-details-btn {
            width: 100%;
            margin-top: 15px;
            background-color: #1976d2;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 4px rgba(25, 118, 210, 0.3);
        }
        .view-details-btn:hover {
            background-color: #1565c0;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(25, 118, 210, 0.4);
        }
        .view-details-btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(25, 118, 210, 0.3);
        }
        </style>
    """