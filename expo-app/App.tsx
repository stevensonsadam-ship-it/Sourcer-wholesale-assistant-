import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from "react-native";
import AutoEstimator from "./components/AutoEstimator";

type RepairItem = {
  key: string;
  label: string;
  amount: number;
  confidence?: number;
  qty?: number;
  unitCost?: number;
  editable?: boolean;
};

type ZipRate = {
  multiplier: number;
  domDays: number;
  discountTrend: number;
  label: string;
};

type ScriptMode = "standard" | "friendly" | "firm" | "agent" | "followup";

const zipRates: Record<string, ZipRate> = {
  "770": { multiplier: 0.9, domDays: 35, discountTrend: -0.02, label: "Houston area" },
  "900": { multiplier: 1.25, domDays: 42, discountTrend: -0.03, label: "Los Angeles area" },
  default: { multiplier: 1.0, domDays: 30, discountTrend: -0.01, label: "National" },
};

export default function App() {
  const [dealId] = useState("deal_" + Date.now());
  const [url, setUrl] = useState("");
  const [address, setAddress] = useState("");
  const [zipcode, setZipcode] = useState("77033");
  const [listPrice, setListPrice] = useState(""); // Current listing price
  const [arv, setArv] = useState("250000");
  const [fee, setFee] = useState("5000");
  const [sqft, setSqft] = useState("1500");
  const [factor, setFactor] = useState(0.65);
  const [risk, setRisk] = useState(0.5);
  const [scriptMode, setScriptMode] = useState<ScriptMode>("standard");

  const [repairItems, setRepairItems] = useState<RepairItem[]>([
    { key: "paint", label: "Interior paint", amount: 1800, qty: 1000, unitCost: 1.8, editable: true },
    { key: "flooring", label: "Flooring (LVP)", amount: 3200, qty: 1000, unitCost: 3.2, editable: true },
    { key: "kitchen", label: "Kitchen refresh", amount: 6500, qty: 1, unitCost: 6500, editable: true },
    { key: "bathroom", label: "Bathroom (x2) refresh", amount: 4500, qty: 1, unitCost: 4500, editable: true },
    { key: "roof", label: "Roof patch/allowance", amount: 2500, qty: 1, unitCost: 2500, editable: true },
    { key: "windows", label: "Windows (allowance)", amount: 1800, qty: 1, unitCost: 1800, editable: true },
    { key: "hvac", label: "HVAC service", amount: 600, qty: 1, unitCost: 600, editable: true },
    { key: "electrical", label: "Electrical/Plumbing misc", amount: 1500, qty: 1, unitCost: 1500, editable: true },
    { key: "trash", label: "Trash/demo/cleanup", amount: 1200, qty: 1, unitCost: 1200, editable: true },
    { key: "contingency", label: "Contingency", amount: 2000, qty: 1, unitCost: 2000, editable: true },
  ]);
  
  const [editingRepairs, setEditingRepairs] = useState(false);

  const getRateForZip = (zip: string): ZipRate => {
    if (zip.length >= 3) {
      const key = zip.substring(0, 3);
      if (zipRates[key]) return zipRates[key];
    }
    return zipRates.default;
  };

  const calculateMAO = (arvVal: number, factorVal: number, repairsVal: number, feeVal: number) => {
    return arvVal * factorVal - repairsVal - feeVal;
  };

  const arvNum = parseFloat(arv) || 0;
  const feeNum = parseFloat(fee) || 0;
  const repairs = repairItems.reduce((sum, item) => sum + item.amount, 0);

  const target = calculateMAO(arvNum, factor, repairs, feeNum);
  const aggressive = calculateMAO(arvNum, Math.max(0.55, factor - 0.03), repairs, feeNum);
  const safe = calculateMAO(arvNum, Math.min(0.75, factor + 0.03), repairs, feeNum);
  const recommended = safe + (aggressive - safe) * risk;

  const rates = getRateForZip(zipcode);

  const handleAutoEstimateApply = (items: RepairItem[]) => {
    // Map backend items to local format
    const mapped = items.map((item) => ({
      key: item.key,
      label: item.label,
      amount: item.amount,
      confidence: item.confidence,
      qty: 1,
      unitCost: item.amount,
      editable: true,
    }));
    setRepairItems(mapped);
    setEditingRepairs(false);
    Alert.alert("Success", `Applied ${items.length} auto-estimated repair items`);
  };

  const updateRepairAmount = (key: string, newAmount: string) => {
    const amount = parseFloat(newAmount) || 0;
    setRepairItems(items => 
      items.map(item => item.key === key ? { ...item, amount } : item)
    );
  };

  const deleteRepairItem = (key: string) => {
    setRepairItems(items => items.filter(item => item.key !== key));
  };

  const addRepairItem = () => {
    const newKey = `custom_${Date.now()}`;
    setRepairItems(items => [
      ...items,
      { key: newKey, label: "New item", amount: 0, qty: 1, unitCost: 0, editable: true }
    ]);
  };

  const updateRepairLabel = (key: string, newLabel: string) => {
    setRepairItems(items => 
      items.map(item => item.key === key ? { ...item, label: newLabel } : item)
    );
  };

  const formatMoney = (val: number) => {
    return "$" + Math.round(val).toLocaleString();
  };

  const getScripts = (mode: ScriptMode): string[] => {
    const factorPct = Math.round(factor * 100);
    switch (mode) {
      case "friendly":
        return [
          `We can make this easy—cash, quick close, no repairs. Based on comps and about ${formatMoney(
            repairs
          )} in work, we're at ${formatMoney(recommended)}.`,
          `Investors use MAO = ARV × Factor − Repairs − Fee. With ARV ≈ ${formatMoney(
            arvNum
          )} and a ${factorPct}% factor, ${formatMoney(recommended)} is fair today.`,
          `If we cover standard closing costs, could ${formatMoney(recommended)} work for you?`,
        ];
      case "firm":
        return [
          `Given the property condition and ${formatMoney(repairs)} in work, our best cash number is ${formatMoney(
            recommended
          )}.`,
          `This is anchored to investor MAO and current DOM (~${rates.domDays} days).`,
          `If we can sign this week, we can hold ${formatMoney(recommended)} firm.`,
        ];
      case "agent":
        return [
          `For your seller: investor buy‑box puts MAO around ${formatMoney(recommended)} assuming ARV ${formatMoney(
            arvNum
          )} and ${formatMoney(repairs)} in renovations.`,
          `We’ll purchase as‑is, no repairs, quick close, and flexible occupancy.`,
          `If your seller needs a clean, certain close, we can EMD tomorrow at ${formatMoney(recommended)}.`,
        ];
      case "followup":
        return [
          `Circling back—market is trending ${Math.round(rates.discountTrend * 100)}%/mo here. If still available, we're at ${formatMoney(
            recommended
          )}.`,
          `Happy to adjust terms (close date, rent‑back, fees) to make ${formatMoney(recommended)} work.`,
          `If there’s a number that would get it done today, let me know and I’ll see if we can match it.`,
        ];
      default:
        return [
          `We're cash, quick close, no repairs. Given the comps and work needed (~${formatMoney(
            repairs
          )}), our number is ${formatMoney(recommended)}.`,
          `Investor pricing uses MAO = ARV × Factor − Repairs − Fee. With ARV ~${formatMoney(
            arvNum
          )} and the current market, we're at ${formatMoney(recommended)}.`,
          `I can be flexible on close date and fees. If we handle all closing costs, would ${formatMoney(
            recommended
          )} work today?`,
        ];
    }
  };

  const renderChip = (mode: ScriptMode, label: string) => (
    <TouchableOpacity
      key={mode}
      onPress={() => setScriptMode(mode)}
      style={[styles.chip, scriptMode === mode && styles.chipSelected]}
    >
      <Text style={[styles.chipText, scriptMode === mode && styles.chipTextSelected]}>{label}</Text>
    </TouchableOpacity>
  );

  const scripts = getScripts(scriptMode);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Sourcer – New Deal</Text>

      {/* Deal Input with Auto-Estimator */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Deal Input</Text>
        
        {/* Auto-Estimator integrated */}
        <View style={styles.autoEstimateSection}>
          <Text style={styles.sectionLabel}>Quick Start: Auto-Estimate from Zillow</Text>
          <AutoEstimator
            dealId={dealId}
            sqft={parseFloat(sqft) || 1500}
            zipcode={zipcode}
            onApply={handleAutoEstimateApply}
          />
          <View style={styles.divider} />
        </View>

        <Text style={styles.sectionLabel}>Or enter manually:</Text>
        <TextInput
          style={styles.input}
          placeholder="Listing URL (Zillow/Redfin/etc)"
          value={url}
          onChangeText={setUrl}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TextInput
          style={styles.input}
          placeholder="Address (optional)"
          value={address}
          onChangeText={setAddress}
        />
        <View style={styles.row}>
          <TextInput
            style={[styles.input, styles.flex1]}
            placeholder="ZIP *"
            value={zipcode}
            onChangeText={setZipcode}
            keyboardType="numeric"
          />
          <View style={styles.spacer} />
          <TextInput
            style={[styles.input, styles.flex1]}
            placeholder="List Price ($)"
            value={listPrice}
            onChangeText={setListPrice}
            keyboardType="numeric"
          />
        </View>
        <View style={styles.row}>
          <TextInput
            style={[styles.input, styles.flex1]}
            placeholder="ARV ($) *"
            value={arv}
            onChangeText={setArv}
            keyboardType="numeric"
          />
          <View style={styles.spacer} />
          <TextInput
            style={[styles.input, styles.flex1]}
            placeholder="Assignment fee ($)"
            value={fee}
            onChangeText={setFee}
            keyboardType="numeric"
          />
        </View>
        <TextInput
          style={styles.input}
          placeholder="Square Feet"
          value={sqft}
          onChangeText={setSqft}
          keyboardType="numeric"
        />
        
        <Text style={styles.label}>Factor: {factor.toFixed(2)} (range: 0.55 - 0.75)</Text>
        <View style={styles.sliderContainer}>
          <TouchableOpacity 
            style={styles.sliderButton}
            onPress={() => setFactor(Math.max(0.55, factor - 0.05))}
          >
            <Text style={styles.sliderButtonText}>−</Text>
          </TouchableOpacity>
          <View style={styles.sliderTrack}>
            <View style={[styles.sliderFill, { width: `${((factor - 0.55) / 0.20) * 100}%` }]} />
          </View>
          <TouchableOpacity 
            style={styles.sliderButton}
            onPress={() => setFactor(Math.min(0.75, factor + 0.05))}
          >
            <Text style={styles.sliderButtonText}>+</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>
          Risk Tolerance: {risk <= 0.33 ? "Safe" : risk >= 0.67 ? "Aggressive" : "Balanced"}
        </Text>
        <View style={styles.sliderContainer}>
          <TouchableOpacity 
            style={styles.sliderButton}
            onPress={() => setRisk(Math.max(0, risk - 0.1))}
          >
            <Text style={styles.sliderButtonText}>−</Text>
          </TouchableOpacity>
          <View style={styles.sliderTrack}>
            <View style={[styles.sliderFill, { width: `${risk * 100}%` }]} />
          </View>
          <TouchableOpacity 
            style={styles.sliderButton}
            onPress={() => setRisk(Math.min(1, risk + 0.1))}
          >
            <Text style={styles.sliderButtonText}>+</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.secondary}>
          Market signals: {rates.label} • DOM ~{rates.domDays} days • price trend{" "}
          {(rates.discountTrend * 100).toFixed(1)}%/mo
        </Text>
      </View>

      {/* Repair Budget */}
      <View style={styles.card}>
        <View style={styles.repairHeader}>
          <Text style={styles.cardTitle}>Repair Budget</Text>
          <TouchableOpacity onPress={() => setEditingRepairs(!editingRepairs)}>
            <Text style={styles.editButton}>{editingRepairs ? "Done" : "Edit"}</Text>
          </TouchableOpacity>
        </View>
        
        {repairItems.map((item) => (
          <View key={item.key} style={styles.repairRow}>
            {editingRepairs ? (
              <>
                <TextInput
                  style={[styles.repairLabel, styles.editableInput]}
                  value={item.label}
                  onChangeText={(text) => updateRepairLabel(item.key, text)}
                  placeholder="Item name"
                />
                <TextInput
                  style={[styles.repairAmountInput]}
                  value={item.amount.toString()}
                  onChangeText={(text) => updateRepairAmount(item.key, text)}
                  keyboardType="numeric"
                  placeholder="0"
                />
                <TouchableOpacity 
                  onPress={() => deleteRepairItem(item.key)}
                  style={styles.deleteButton}
                >
                  <Text style={styles.deleteButtonText}>✕</Text>
                </TouchableOpacity>
              </>
            ) : (
              <>
                <Text style={styles.repairLabel}>{item.label}</Text>
                <Text style={styles.repairAmount}>{formatMoney(item.amount)}</Text>
              </>
            )}
          </View>
        ))}
        
        {editingRepairs && (
          <TouchableOpacity onPress={addRepairItem} style={styles.addButton}>
            <Text style={styles.addButtonText}>+ Add Item</Text>
          </TouchableOpacity>
        )}
        
        <View style={styles.divider} />
        <View style={styles.repairRow}>
          <Text style={styles.totalLabel}>Repairs total</Text>
          <Text style={styles.totalAmount}>{formatMoney(repairs)}</Text>
        </View>
      </View>

      {/* Offer Range */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Offer Range (MAO = ARV × Factor − Repairs − Fee)</Text>
        
        {/* Warning if MAO exceeds list price */}
        {listPrice && parseFloat(listPrice) > 0 && recommended > parseFloat(listPrice) && (
          <View style={styles.warningBox}>
            <Text style={styles.warningText}>
              ⚠️ Warning: Your recommended offer ({formatMoney(recommended)}) is higher than the list price ({formatMoney(parseFloat(listPrice))})!
              {"\n"}• Check ARV - should be AFTER REPAIR value (higher than list)
              {"\n"}• Adjust Factor down (currently {(factor * 100).toFixed(0)}%)
              {"\n"}• Verify repair costs aren't too low
            </Text>
          </View>
        )}
        
        {/* Show list price comparison */}
        {listPrice && parseFloat(listPrice) > 0 && (
          <View style={styles.comparisonRow}>
            <Text style={styles.comparisonLabel}>List Price:</Text>
            <Text style={styles.comparisonValue}>{formatMoney(parseFloat(listPrice))}</Text>
          </View>
        )}
        
        <View style={[styles.offerCard, styles.aggressive]}>
          <Text style={styles.offerLabel}>Aggressive</Text>
          <Text style={styles.offerAmount}>{formatMoney(aggressive)}</Text>
        </View>
        <View style={[styles.offerCard, styles.target]}>
          <Text style={styles.offerLabel}>Target</Text>
          <Text style={styles.offerAmount}>{formatMoney(target)}</Text>
        </View>
        <View style={[styles.offerCard, styles.safe]}>
          <Text style={styles.offerLabel}>Safe</Text>
          <Text style={styles.offerAmount}>{formatMoney(safe)}</Text>
        </View>
        <View style={styles.recommendedRow}>
          <Text style={styles.totalLabel}>Recommended (by risk slider)</Text>
          <Text style={styles.totalAmount}>{formatMoney(recommended)}</Text>
        </View>
        
        {/* Show discount from list price */}
        {listPrice && parseFloat(listPrice) > 0 && (
          <View style={styles.discountRow}>
            <Text style={styles.discountLabel}>
              {recommended < parseFloat(listPrice) ? "✓ Below List by:" : "❌ Above List by:"}
            </Text>
            <Text style={[
              styles.discountValue,
              recommended < parseFloat(listPrice) ? styles.discountGood : styles.discountBad
            ]}>
              {formatMoney(Math.abs(parseFloat(listPrice) - recommended))} 
              ({Math.abs(((parseFloat(listPrice) - recommended) / parseFloat(listPrice)) * 100).toFixed(1)}%)
            </Text>
          </View>
        )}
      </View>

      {/* Negotiation Scripts */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Negotiation Scripts</Text>
        <View style={styles.chipRow}>
          {renderChip("standard", "Standard")}
          {renderChip("friendly", "Friendly")}
          {renderChip("firm", "Firm")}
          {renderChip("agent", "Agent")}
          {renderChip("followup", "Follow-up")}
        </View>
        {scripts.map((line, idx) => (
          <Text key={idx} style={styles.script}>• {line}</Text>
        ))}
      </View>

      {/* Action Buttons */}
      <View style={styles.buttonRow}>
        <TouchableOpacity style={[styles.button, styles.primaryButton]}>
          <Text style={styles.buttonText}>Save to Pipeline</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.button, styles.secondaryButton]}>
          <Text style={styles.buttonText}>PDF / Share</Text>
        </TouchableOpacity>
      </View>

      {/* Disclaimer */}
      <Text style={styles.disclaimer}>
        Disclaimer: All values are estimates for investor due diligence only. ARV, comps, and repair budgets
        should be verified by licensed professionals. Market data and pricing multipliers are placeholders.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginVertical: 16,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    fontSize: 14,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
  },
  flex1: {
    flex: 1,
  },
  spacer: {
    width: 12,
  },
  label: {
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 8,
  },
  secondary: {
    fontSize: 12,
    color: "#666",
    marginTop: 8,
  },
  repairRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
  },
  repairLabel: {
    fontSize: 14,
    flex: 1,
  },
  repairAmount: {
    fontSize: 14,
    fontWeight: "600",
  },
  divider: {
    height: 1,
    backgroundColor: "#e0e0e0",
    marginVertical: 8,
  },
  totalLabel: {
    fontSize: 16,
    fontWeight: "700",
  },
  totalAmount: {
    fontSize: 18,
    fontWeight: "800",
  },
  offerCard: {
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
    flexDirection: "row",
    justifyContent: "space-between",
    borderWidth: 1,
  },
  aggressive: {
    backgroundColor: "#ffebee",
    borderColor: "#ef5350",
  },
  target: {
    backgroundColor: "#fff3e0",
    borderColor: "#ff9800",
  },
  safe: {
    backgroundColor: "#e8f5e9",
    borderColor: "#66bb6a",
  },
  offerLabel: {
    fontSize: 16,
    fontWeight: "700",
  },
  offerAmount: {
    fontSize: 18,
    fontWeight: "800",
  },
  recommendedRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
  },
  script: {
    fontSize: 14,
    marginBottom: 8,
    lineHeight: 20,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  primaryButton: {
    backgroundColor: "#673ab7",
  },
  secondaryButton: {
    backgroundColor: "#9c27b0",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  disclaimer: {
    fontSize: 12,
    color: "#666",
    lineHeight: 18,
    marginBottom: 24,
  },
  sliderContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
    gap: 8,
  },
  sliderButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "#673ab7",
    justifyContent: "center",
    alignItems: "center",
  },
  sliderButtonText: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "bold",
  },
  sliderTrack: {
    flex: 1,
    height: 8,
    backgroundColor: "#e0e0e0",
    borderRadius: 4,
    overflow: "hidden",
  },
  sliderFill: {
    height: "100%",
    backgroundColor: "#673ab7",
  },
  repairHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  editButton: {
    color: "#673ab7",
    fontSize: 16,
    fontWeight: "600",
  },
  editableInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 4,
    padding: 4,
    marginRight: 8,
  },
  repairAmountInput: {
    width: 100,
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 4,
    padding: 4,
    fontSize: 14,
    fontWeight: "600",
    textAlign: "right",
  },
  deleteButton: {
    width: 32,
    height: 32,
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 8,
  },
  deleteButtonText: {
    color: "#f44336",
    fontSize: 20,
    fontWeight: "bold",
  },
  addButton: {
    padding: 12,
    backgroundColor: "#f5f5f5",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#ddd",
    borderStyle: "dashed",
    alignItems: "center",
    marginVertical: 8,
  },
  addButtonText: {
    color: "#673ab7",
    fontSize: 14,
    fontWeight: "600",
  },
  autoEstimateSection: {
    marginBottom: 16,
    padding: 12,
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#666",
    marginBottom: 8,
  },
  chipRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  chip: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 16,
    backgroundColor: "#eee",
    borderWidth: 1,
    borderColor: "#ddd",
  },
  chipSelected: {
    backgroundColor: "#673ab7",
    borderColor: "#673ab7",
  },
  chipText: {
    fontSize: 12,
    color: "#333",
    fontWeight: "600",
  },
  chipTextSelected: {
    color: "#fff",
  },
  warningBox: {
    backgroundColor: "#fff3cd",
    borderLeftWidth: 4,
    borderLeftColor: "#ff9800",
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  warningText: {
    color: "#856404",
    fontSize: 13,
    lineHeight: 20,
  },
  comparisonRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 12,
    backgroundColor: "#f5f5f5",
    borderRadius: 8,
    marginBottom: 12,
  },
  comparisonLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#666",
  },
  comparisonValue: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#333",
  },
  discountRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 12,
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
    marginTop: 12,
    borderWidth: 1,
    borderColor: "#e0e0e0",
  },
  discountLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#666",
  },
  discountValue: {
    fontSize: 16,
    fontWeight: "bold",
  },
  discountGood: {
    color: "#4caf50",
  },
  discountBad: {
    color: "#f44336",
  },
});
