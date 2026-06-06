-- AirDosa Supabase schema
-- Run this in Supabase Dashboard → SQL Editor → New query

CREATE TABLE IF NOT EXISTS orders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  order_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  address TEXT NOT NULL,
  dosa_type TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity >= 1 AND quantity <= 10),
  plan TEXT NOT NULL CHECK (plan IN ('starter', 'dosa-pass')),
  status TEXT NOT NULL DEFAULT 'confirmed',
  status_history JSONB NOT NULL DEFAULT '[]'::jsonb,
  price INTEGER NOT NULL DEFAULT 0,
  eta_minutes INTEGER NOT NULL,
  estimated_delivery TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  subscription_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  plan TEXT NOT NULL DEFAULT 'dosa-pass',
  price INTEGER NOT NULL DEFAULT 499,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders (order_id);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_subscriptions_subscription_id ON subscriptions (subscription_id);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Backend uses service_role key (server-side only). No public policies needed.
