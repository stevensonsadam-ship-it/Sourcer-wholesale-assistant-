import React, { useState } from "react";
import { View, TextInput, Button, ActivityIndicator, Alert } from "react-native";

type RepairItem = {
  key: string;          // e.g., "interior_paint"
  label: string;        // e.g., "Interior paint"
  amount: number;       // dollars
  confidence?: number;  // 0..1
};

export default function AutoEstimator({
  dealId,
  sqft,
  zipcode,
  onApply, // (items: RepairItem[]) => void  --> parent fills the UI rows
}: {
  dealId: string;
  sqft: number;
  zipcode: string;
  onApply: (items: RepairItem[]) => void;
}) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAutoEstimate = async () => {
    if (!url) return Alert.alert("Paste a Zillow link first");
    setLoading(true);
    try {
      const res = await fetch(process.env.EXPO_PUBLIC_API_BASE + "/api/estimateFromZillow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, sqft, zipcode, dealId }),
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || "Failed to estimate");
      }
      const data: { items: RepairItem[] } = await res.json();
      onApply(data.items);
    } catch (e: any) {
      Alert.alert("Auto-estimate failed", e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ gap: 12 }}>
      <TextInput
        placeholder="Paste Zillow link"
        autoCapitalize="none"
        autoCorrect={false}
        value={url}
        onChangeText={setUrl}
        style={{ borderWidth: 1, borderRadius: 8, padding: 10, borderColor: "#ccc" }}
      />
      {loading ? (
        <ActivityIndicator />
      ) : (
        <Button title="Auto-estimate repairs" onPress={handleAutoEstimate} />
      )}
    </View>
  );
}
