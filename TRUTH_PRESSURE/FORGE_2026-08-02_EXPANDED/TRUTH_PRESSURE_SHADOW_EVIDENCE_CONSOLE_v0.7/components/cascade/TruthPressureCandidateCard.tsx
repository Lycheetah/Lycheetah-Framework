import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import type { AppTruthPressureViewModel } from '../../lib/truth-pressure-rc/index.ts';

export type TruthPressureCandidateCardProps = {
  view: AppTruthPressureViewModel;
  developerLabel?: string;
};

function percent(value: number): string {
  return `${Math.round(value * 1000) / 10}%`;
}

/**
 * Neutral developer/research preview.
 *
 * This component intentionally avoids true/false colors and does not expose a
 * structural action for text triage.
 */
export function TruthPressureCandidateCard({
  view,
  developerLabel = 'RESEARCH PREVIEW',
}: TruthPressureCandidateCardProps) {
  return (
    <View style={styles.card} accessibilityRole="summary">
      <Text style={styles.eyebrow}>{developerLabel}</Text>
      <Text style={styles.title}>{view.headline.label}</Text>
      <Text style={styles.index}>{percent(view.headline.value)}</Text>
      <Text style={styles.unit}>{view.headline.unit}</Text>

      <View style={styles.componentList}>
        {view.components.map(component => (
          <View key={component.key} style={styles.componentRow}>
            <View style={styles.componentHeading}>
              <Text style={styles.componentKey}>{component.key}</Text>
              <Text style={styles.componentLabel}>{component.label}</Text>
            </View>
            <Text style={styles.componentValue}>{percent(component.value)}</Text>
            <Text style={styles.componentMeaning}>{component.meaning}</Text>
          </View>
        ))}
      </View>

      <View style={styles.reviewBox}>
        <Text style={styles.reviewTitle}>{view.review.state.replaceAll('_', ' ')}</Text>
        <Text style={styles.body}>{view.review.message}</Text>
      </View>

      {view.warnings.length > 0 && (
        <View style={styles.warningBox}>
          <Text style={styles.warningTitle}>Limits and warnings</Text>
          {view.warnings.slice(0, 5).map((warning, index) => (
            <Text key={`${index}-${warning}`} style={styles.body}>• {warning}</Text>
          ))}
        </View>
      )}

      <Text style={styles.boundary}>{view.headline.disclaimer}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderWidth: 1,
    borderColor: '#3f3f46',
    borderRadius: 16,
    padding: 16,
    gap: 8,
    backgroundColor: '#111114',
  },
  eyebrow: {
    fontSize: 11,
    letterSpacing: 1.4,
    color: '#a1a1aa',
    fontWeight: '700',
  },
  title: {
    fontSize: 18,
    color: '#f4f4f5',
    fontWeight: '700',
  },
  index: {
    fontSize: 34,
    color: '#f4f4f5',
    fontWeight: '800',
  },
  unit: {
    fontSize: 12,
    color: '#a1a1aa',
  },
  componentList: {
    gap: 10,
    marginTop: 6,
  },
  componentRow: {
    borderTopWidth: 1,
    borderTopColor: '#27272a',
    paddingTop: 10,
    gap: 4,
  },
  componentHeading: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  componentKey: {
    width: 22,
    fontWeight: '800',
    color: '#e4e4e7',
  },
  componentLabel: {
    color: '#e4e4e7',
    fontWeight: '600',
  },
  componentValue: {
    color: '#fafafa',
    fontSize: 17,
    fontWeight: '700',
  },
  componentMeaning: {
    color: '#a1a1aa',
    lineHeight: 18,
  },
  reviewBox: {
    marginTop: 6,
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#1c1c20',
    gap: 4,
  },
  reviewTitle: {
    color: '#d4d4d8',
    fontWeight: '700',
    fontSize: 12,
  },
  warningBox: {
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#52525b',
    gap: 4,
  },
  warningTitle: {
    color: '#e4e4e7',
    fontWeight: '700',
  },
  body: {
    color: '#c4c4cc',
    lineHeight: 19,
  },
  boundary: {
    marginTop: 4,
    color: '#d4d4d8',
    fontSize: 12,
    lineHeight: 18,
    fontStyle: 'italic',
  },
});
