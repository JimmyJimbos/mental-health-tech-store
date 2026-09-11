export type ItemStatus = 'in_stock' | 'listed' | 'sold';

export type InventoryItem = {
  id: string;
  name: string;
  category: string;
  buyPrice: number;
  sellPrice: number | null;
  status: ItemStatus;
  buyDate: string;
  soldDate: string | null;
};

const STORAGE_KEY = 'flip-assistant.inventory.v1';

export function loadInventory(): InventoryItem[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as InventoryItem[]) : [];
  } catch {
    return [];
  }
}

export function saveInventory(items: InventoryItem[]): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

export function isSameMonth(dateIso: string, reference: Date): boolean {
  const d = new Date(dateIso);
  return d.getFullYear() === reference.getFullYear() && d.getMonth() === reference.getMonth();
}
