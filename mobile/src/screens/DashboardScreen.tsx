/**
 * Dashboard Screen
 * Main dashboard with metrics and insights
 */
import React, { useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchDashboardData, fetchAlerts } from '../store/slices/dashboardSlice';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const DashboardScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { metrics, alerts, news, loading } = useAppSelector((state) => state.dashboard);

  useEffect(() => {
    if (user) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = () => {
    if (user) {
      dispatch(fetchDashboardData(user.id));
      dispatch(fetchAlerts(user.id));
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      default:
        return '#2196F3';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={loadDashboardData} />
      }
    >
      {/* Welcome Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>Welcome back,</Text>
        <Text style={styles.userName}>{user?.name}</Text>
      </View>

      {/* Metrics Cards */}
      <View style={styles.metricsContainer}>
        <View style={styles.metricCard}>
          <Icon name="trending-up" size={24} color="#4CAF50" />
          <Text style={styles.metricValue}>
            {metrics ? formatCurrency(metrics.revenue) : '-'}
          </Text>
          <Text style={styles.metricLabel}>Revenue</Text>
          {metrics && (
            <Text style={[styles.metricChange, { color: metrics.revenue_growth >= 0 ? '#4CAF50' : '#f44336' }]}>
              {metrics.revenue_growth >= 0 ? '+' : ''}{metrics.revenue_growth.toFixed(1)}%
            </Text>
          )}
        </View>

        <View style={styles.metricCard}>
          <Icon name="cash" size={24} color="#2196F3" />
          <Text style={styles.metricValue}>
            {metrics ? formatCurrency(metrics.cash_balance) : '-'}
          </Text>
          <Text style={styles.metricLabel}>Cash Balance</Text>
          {metrics && (
            <Text style={styles.metricSubtext}>
              {metrics.runway_months} months runway
            </Text>
          )}
        </View>

        <View style={styles.metricCard}>
          <Icon name="account-group" size={24} color="#9C27B0" />
          <Text style={styles.metricValue}>{metrics?.customer_count || 0}</Text>
          <Text style={styles.metricLabel}>Customers</Text>
          {metrics && (
            <Text style={styles.metricSubtext}>
              {formatCurrency(metrics.mrr)} MRR
            </Text>
          )}
        </View>

        <View style={styles.metricCard}>
          <Icon name="fire" size={24} color="#FF5722" />
          <Text style={styles.metricValue}>
            {metrics ? formatCurrency(metrics.burn_rate) : '-'}
          </Text>
          <Text style={styles.metricLabel}>Burn Rate</Text>
          <Text style={styles.metricSubtext}>Monthly</Text>
        </View>
      </View>

      {/* Alerts */}
      {alerts.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Alerts</Text>
          {alerts.map((alert) => (
            <View
              key={alert.id}
              style={[styles.alertCard, { borderLeftColor: getAlertColor(alert.type) }]}
            >
              <View style={styles.alertHeader}>
                <Text style={styles.alertTitle}>{alert.title}</Text>
                <Text style={styles.alertType}>{alert.type.toUpperCase()}</Text>
              </View>
              <Text style={styles.alertMessage}>{alert.message}</Text>
              <Text style={styles.alertTime}>
                {new Date(alert.timestamp).toLocaleDateString()}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* News Feed */}
      {news.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Latest News</Text>
          {news.map((item) => (
            <TouchableOpacity key={item.id} style={styles.newsCard}>
              <Text style={styles.newsTitle}>{item.title}</Text>
              <Text style={styles.newsSummary} numberOfLines={2}>
                {item.summary}
              </Text>
              <View style={styles.newsFooter}>
                <Text style={styles.newsSource}>{item.source}</Text>
                <View style={[styles.sentimentBadge, { backgroundColor: getSentimentColor(item.sentiment) }]}>
                  <Text style={styles.sentimentText}>{item.sentiment}</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

const getSentimentColor = (sentiment: string) => {
  switch (sentiment) {
    case 'positive':
      return '#4CAF50';
    case 'negative':
      return '#f44336';
    default:
      return '#9E9E9E';
  }
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#2196F3',
    padding: 24,
    paddingTop: 16,
  },
  greeting: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 4,
  },
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 12,
  },
  metricCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    width: '48%',
    margin: '1%',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  metricLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  metricChange: {
    fontSize: 12,
    marginTop: 4,
    fontWeight: 'bold',
  },
  metricSubtext: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  alertType: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#666',
  },
  alertMessage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  alertTime: {
    fontSize: 12,
    color: '#999',
  },
  newsCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  newsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  newsSummary: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  newsFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  newsSource: {
    fontSize: 12,
    color: '#999',
  },
  sentimentBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  sentimentText: {
    fontSize: 10,
    color: '#fff',
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
});

export default DashboardScreen;
