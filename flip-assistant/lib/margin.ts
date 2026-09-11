export type Platform = 'ebay' | 'vinted';

export type MarginInput = {
  platform: Platform;
  buyPrice: number;
  sellPrice: number;
  shippingCost: number;
  ebayFeePct: number;
  ebayFixedFee: number;
};

export type MarginResult = {
  fees: number;
  netProceeds: number;
  profit: number;
  marginPct: number;
};

/**
 * Vinted charges its "buyer protection fee" on top of the listed price, paid by the
 * buyer — the seller receives the full listed sell price. eBay deducts a final value
 * fee (percentage + small fixed fee per order) from what the seller receives.
 */
export function calculateMargin(input: MarginInput): MarginResult {
  const { platform, buyPrice, sellPrice, shippingCost, ebayFeePct, ebayFixedFee } = input;

  const fees = platform === 'ebay' ? (sellPrice * ebayFeePct) / 100 + ebayFixedFee : 0;

  const netProceeds = sellPrice - fees - shippingCost;
  const profit = netProceeds - buyPrice;
  const marginPct = buyPrice > 0 ? (profit / buyPrice) * 100 : 0;

  return { fees, netProceeds, profit, marginPct };
}
