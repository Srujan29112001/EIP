"""
Financial Forecasting Model
Predicts revenue, expenses, and financial metrics for entrepreneurs
"""
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler
import joblib


class LSTMForecaster(nn.Module):
    """
    LSTM-based financial forecasting model
    Predicts future financial metrics based on historical data
    """

    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, output_size: int = 1):
        """
        Initialize LSTM forecaster

        Args:
            input_size: Number of input features
            hidden_size: LSTM hidden state size
            num_layers: Number of LSTM layers
            output_size: Number of output predictions
        """
        super(LSTMForecaster, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )

        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden_size // 2, output_size)

    def forward(self, x):
        """Forward pass"""
        # LSTM
        lstm_out, _ = self.lstm(x)

        # Take the last time step
        last_time_step = lstm_out[:, -1, :]

        # Fully connected layers
        out = self.fc1(last_time_step)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)

        return out


class FinancialForecaster:
    """
    Financial forecasting service for entrepreneurs
    Predicts revenue, expenses, cash flow, and runway
    """

    def __init__(self, model_path: str = None):
        """
        Initialize forecaster

        Args:
            model_path: Path to trained model weights
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = StandardScaler()
        self.model = None
        self.model_path = model_path

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str):
        """Load trained model"""
        checkpoint = torch.load(model_path, map_location=self.device)

        # Initialize model with saved config
        config = checkpoint.get("config", {})
        self.model = LSTMForecaster(
            input_size=config.get("input_size", 10),
            hidden_size=config.get("hidden_size", 128),
            num_layers=config.get("num_layers", 2),
            output_size=config.get("output_size", 1)
        )

        # Load weights
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.to(self.device)
        self.model.eval()

        # Load scaler
        if "scaler" in checkpoint:
            self.scaler = checkpoint["scaler"]

    def forecast_revenue(
        self,
        historical_data: pd.DataFrame,
        periods_ahead: int = 6
    ) -> Dict[str, Any]:
        """
        Forecast future revenue

        Args:
            historical_data: DataFrame with columns: date, revenue, marketing_spend, etc.
            periods_ahead: Number of periods to forecast

        Returns:
            Dict with forecasts and confidence intervals
        """
        # Prepare data
        features = self._prepare_features(historical_data)

        # Make predictions
        predictions = []
        confidence_intervals = []

        for _ in range(periods_ahead):
            # Predict next period
            pred = self._predict_next(features)
            predictions.append(pred)

            # Calculate confidence interval (simplified)
            std = np.std(predictions) if len(predictions) > 1 else pred * 0.1
            ci_lower = pred - 1.96 * std
            ci_upper = pred + 1.96 * std
            confidence_intervals.append((ci_lower, ci_upper))

            # Update features for next prediction
            features = self._update_features(features, pred)

        # Calculate growth rates
        current_revenue = historical_data['revenue'].iloc[-1]
        forecasted_revenue = predictions[-1]
        growth_rate = ((forecasted_revenue - current_revenue) / current_revenue) * 100

        return {
            "forecasts": predictions,
            "confidence_intervals": confidence_intervals,
            "current_revenue": current_revenue,
            "forecasted_revenue": forecasted_revenue,
            "growth_rate": growth_rate,
            "periods": periods_ahead,
            "trend": "increasing" if growth_rate > 0 else "decreasing"
        }

    def forecast_runway(
        self,
        current_cash: float,
        monthly_burn_rate: float,
        historical_revenue: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Forecast cash runway for startup

        Args:
            current_cash: Current cash balance
            monthly_burn_rate: Average monthly burn rate
            historical_revenue: Historical revenue data

        Returns:
            Dict with runway analysis
        """
        # Forecast revenue growth
        revenue_forecast = self.forecast_revenue(historical_revenue, periods_ahead=12)

        # Calculate month-by-month cash flow
        cash_balance = current_cash
        months = []

        for month in range(12):
            forecasted_revenue = revenue_forecast["forecasts"][month] if month < len(revenue_forecast["forecasts"]) else revenue_forecast["forecasts"][-1]

            # Monthly cash flow = revenue - burn rate
            monthly_cash_flow = forecasted_revenue - monthly_burn_rate
            cash_balance += monthly_cash_flow

            months.append({
                "month": month + 1,
                "cash_balance": max(cash_balance, 0),
                "revenue": forecasted_revenue,
                "burn_rate": monthly_burn_rate,
                "cash_flow": monthly_cash_flow
            })

            # Check if runway ended
            if cash_balance <= 0:
                break

        # Calculate runway in months
        runway_months = len([m for m in months if m["cash_balance"] > 0])

        return {
            "current_cash": current_cash,
            "monthly_burn_rate": monthly_burn_rate,
            "runway_months": runway_months,
            "runway_status": self._classify_runway(runway_months),
            "monthly_projections": months,
            "recommendations": self._get_runway_recommendations(runway_months)
        }

    def forecast_breakeven(
        self,
        historical_data: pd.DataFrame,
        fixed_costs: float,
        variable_cost_ratio: float
    ) -> Dict[str, Any]:
        """
        Forecast when business will reach breakeven

        Args:
            historical_data: Historical financial data
            fixed_costs: Monthly fixed costs
            variable_cost_ratio: Variable costs as % of revenue

        Returns:
            Dict with breakeven analysis
        """
        revenue_forecast = self.forecast_revenue(historical_data, periods_ahead=24)

        breakeven_month = None
        cumulative_profit = 0

        for month, revenue in enumerate(revenue_forecast["forecasts"]):
            # Calculate profit
            variable_costs = revenue * variable_cost_ratio
            total_costs = fixed_costs + variable_costs
            monthly_profit = revenue - total_costs
            cumulative_profit += monthly_profit

            # Check if breakeven reached
            if cumulative_profit >= 0 and breakeven_month is None:
                breakeven_month = month + 1

        return {
            "breakeven_month": breakeven_month,
            "breakeven_revenue": revenue_forecast["forecasts"][breakeven_month - 1] if breakeven_month else None,
            "fixed_costs": fixed_costs,
            "variable_cost_ratio": variable_cost_ratio,
            "status": "achievable" if breakeven_month and breakeven_month <= 24 else "delayed",
            "recommendation": self._get_breakeven_recommendation(breakeven_month)
        }

    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for model input"""
        # Use simple features for now
        features = data[['revenue']].values[-6:]  # Last 6 periods
        return features

    def _predict_next(self, features: np.ndarray) -> float:
        """Predict next period"""
        if self.model is None:
            # Fallback: simple linear extrapolation
            if len(features) >= 2:
                trend = features[-1] - features[-2]
                return float(features[-1] + trend)
            return float(features[-1])

        # Use trained model
        with torch.no_grad():
            x = torch.FloatTensor(features).unsqueeze(0).to(self.device)
            pred = self.model(x)
            return pred.item()

    def _update_features(self, features: np.ndarray, new_value: float) -> np.ndarray:
        """Update features with new prediction"""
        return np.append(features[1:], new_value)

    def _classify_runway(self, months: int) -> str:
        """Classify runway status"""
        if months < 3:
            return "critical"
        elif months < 6:
            return "warning"
        elif months < 12:
            return "healthy"
        else:
            return "strong"

    def _get_runway_recommendations(self, months: int) -> List[str]:
        """Get recommendations based on runway"""
        if months < 3:
            return [
                "URGENT: Seek immediate funding or bridge loan",
                "Cut non-essential expenses immediately",
                "Accelerate revenue generation activities",
                "Consider emergency cost reduction measures"
            ]
        elif months < 6:
            return [
                "Begin fundraising process now",
                "Review and optimize operational expenses",
                "Focus on revenue growth initiatives",
                "Prepare financial projections for investors"
            ]
        elif months < 12:
            return [
                "Plan fundraising timeline for next 3-6 months",
                "Continue monitoring burn rate closely",
                "Invest in sustainable growth",
                "Build strategic cash reserves"
            ]
        else:
            return [
                "Maintain healthy cash management practices",
                "Consider strategic investments for growth",
                "Build contingency reserves",
                "Optimize capital allocation"
            ]

    def _get_breakeven_recommendation(self, months: int) -> str:
        """Get breakeven recommendation"""
        if months is None:
            return "Breakeven not achievable with current trajectory. Consider pivoting business model or reducing costs."
        elif months <= 12:
            return f"On track to breakeven in {months} months. Continue current strategy."
        elif months <= 24:
            return f"Breakeven projected in {months} months. Consider accelerating revenue growth or reducing costs."
        else:
            return "Breakeven timeline is extended. Recommend reviewing business model and unit economics."


# Export
__all__ = ["LSTMForecaster", "FinancialForecaster"]
