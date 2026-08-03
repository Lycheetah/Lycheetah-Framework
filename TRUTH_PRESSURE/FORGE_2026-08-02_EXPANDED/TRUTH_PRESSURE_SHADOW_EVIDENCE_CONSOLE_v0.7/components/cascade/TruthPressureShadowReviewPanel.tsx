import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useTruthPressureShadowReview } from '../../hooks/useTruthPressureShadowReview.ts';

type Props = {
  onExportJson?: (content: string) => void | Promise<void>;
  onExportMarkdown?: (content: string) => void | Promise<void>;
  allowClear?: boolean;
};

function pct(value: number | null): string {
  return value === null ? 'n/a' : `${Math.round(value * 1000) / 10}%`;
}

export function TruthPressureShadowReviewPanel({
  onExportJson,
  onExportMarkdown,
  allowClear = false,
}: Props) {
  const review = useTruthPressureShadowReview();

  if (review.loading && !review.report) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
        <Text style={styles.muted}>Loading Truth Pressure shadow evidence…</Text>
      </View>
    );
  }

  if (review.error) {
    return (
      <View style={styles.card}>
        <Text style={styles.title}>Shadow evidence unavailable</Text>
        <Text style={styles.muted}>{review.error}</Text>
        <Pressable style={styles.button} onPress={() => void review.refresh()}>
          <Text style={styles.buttonText}>Retry</Text>
        </Pressable>
      </View>
    );
  }

  const report = review.report;
  if (!report) return null;

  const exportJson = review.exportJson();
  const exportMarkdown = review.exportMarkdown();

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.eyebrow}>TRUTH PRESSURE RESEARCH CONSOLE</Text>
      <Text style={styles.heading}>Shadow evidence</Text>
      <Text style={styles.boundary}>
        Engineering evidence only. This console does not establish scientific validity.
      </Text>

      <View style={styles.card}>
        <Text style={styles.state}>{report.releaseState.replaceAll('_', ' ')}</Text>
        <Text style={styles.big}>{report.summary.total}/100</Text>
        <Text style={styles.muted}>privacy-safe comparisons collected</Text>
      </View>

      <View style={styles.grid}>
        <Metric label="Candidate mean" value={pct(report.summary.meanCandidatePressure)} />
        <Metric label="Legacy mean" value={pct(report.summary.meanLegacyPressure)} />
        <Metric label="Warnings" value={String(report.summary.candidateWarnings)} />
        <Metric label="Trigger disagreements" value={String(report.summary.triggerDisagreements)} />
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>Engineering gates</Text>
        {report.gates.map(gate => (
          <View key={gate.id} style={styles.row}>
            <Text style={styles.gateState}>{gate.state}</Text>
            <View style={styles.flex}>
              <Text style={styles.rowTitle}>{gate.label}</Text>
              <Text style={styles.muted}>{gate.detail}</Text>
            </View>
          </View>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>Candidate pressure distribution</Text>
        {report.pressureBins.map(bin => (
          <View key={bin.label} style={styles.simpleRow}>
            <Text style={styles.muted}>{bin.label}</Text>
            <Text style={styles.value}>{bin.count}</Text>
          </View>
        ))}
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>Most frequent warnings</Text>
        {report.warningFrequencies.length === 0 ? (
          <Text style={styles.muted}>No warnings recorded.</Text>
        ) : report.warningFrequencies.slice(0, 8).map(item => (
          <View key={item.warning} style={styles.warning}>
            <Text style={styles.rowTitle}>{item.count} · {pct(item.share)}</Text>
            <Text style={styles.muted}>{item.warning}</Text>
          </View>
        ))}
      </View>

      <View style={styles.actions}>
        <Pressable
          style={styles.button}
          disabled={!exportJson || !onExportJson}
          onPress={() => exportJson && onExportJson?.(exportJson)}
        >
          <Text style={styles.buttonText}>Export JSON</Text>
        </Pressable>
        <Pressable
          style={styles.button}
          disabled={!exportMarkdown || !onExportMarkdown}
          onPress={() => exportMarkdown && onExportMarkdown?.(exportMarkdown)}
        >
          <Text style={styles.buttonText}>Export report</Text>
        </Pressable>
        <Pressable style={styles.button} onPress={() => void review.refresh()}>
          <Text style={styles.buttonText}>Refresh</Text>
        </Pressable>
        {allowClear && (
          <Pressable style={styles.dangerButton} onPress={() => void review.clear()}>
            <Text style={styles.buttonText}>Clear local evidence</Text>
          </Pressable>
        )}
      </View>
    </ScrollView>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.metric}>
      <Text style={styles.value}>{value}</Text>
      <Text style={styles.muted}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    gap: 12,
    backgroundColor: '#09090b',
  },
  center: {
    minHeight: 160,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  eyebrow: {
    color: '#a1a1aa',
    fontSize: 11,
    letterSpacing: 1.4,
    fontWeight: '700',
  },
  heading: {
    color: '#fafafa',
    fontSize: 28,
    fontWeight: '800',
  },
  boundary: {
    color: '#d4d4d8',
    lineHeight: 19,
    fontStyle: 'italic',
  },
  card: {
    backgroundColor: '#18181b',
    borderWidth: 1,
    borderColor: '#3f3f46',
    borderRadius: 14,
    padding: 14,
    gap: 10,
  },
  title: {
    color: '#f4f4f5',
    fontSize: 17,
    fontWeight: '700',
  },
  state: {
    color: '#d4d4d8',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 1,
  },
  big: {
    color: '#fafafa',
    fontSize: 36,
    fontWeight: '800',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  metric: {
    minWidth: '46%',
    flexGrow: 1,
    backgroundColor: '#18181b',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#27272a',
  },
  value: {
    color: '#fafafa',
    fontWeight: '800',
    fontSize: 18,
  },
  muted: {
    color: '#a1a1aa',
    lineHeight: 18,
  },
  row: {
    flexDirection: 'row',
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: '#27272a',
    paddingTop: 10,
  },
  simpleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: '#27272a',
    paddingTop: 8,
  },
  gateState: {
    width: 48,
    color: '#e4e4e7',
    fontWeight: '800',
  },
  flex: {
    flex: 1,
  },
  rowTitle: {
    color: '#e4e4e7',
    fontWeight: '700',
  },
  warning: {
    borderTopWidth: 1,
    borderTopColor: '#27272a',
    paddingTop: 8,
    gap: 3,
  },
  actions: {
    gap: 8,
  },
  button: {
    backgroundColor: '#27272a',
    borderRadius: 10,
    paddingVertical: 11,
    paddingHorizontal: 14,
    alignItems: 'center',
  },
  dangerButton: {
    backgroundColor: '#3f1d24',
    borderRadius: 10,
    paddingVertical: 11,
    paddingHorizontal: 14,
    alignItems: 'center',
  },
  buttonText: {
    color: '#f4f4f5',
    fontWeight: '700',
  },
});
