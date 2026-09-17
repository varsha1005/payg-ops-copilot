-- PAYG Ops Copilot: sample analytics queries
-- Assumes a table called support_tickets with the same fields as data/synthetic_tickets.csv.

-- 1) Product adoption: how often is AI triage used by market?
SELECT
    market,
    COUNT(*) AS total_tickets,
    SUM(ai_used) AS ai_triaged_tickets,
    ROUND(100.0 * SUM(ai_used) / COUNT(*), 1) AS ai_adoption_pct
FROM support_tickets
GROUP BY market
ORDER BY ai_adoption_pct DESC;

-- 2) Quality: where do people override AI decisions?
SELECT
    category,
    SUM(CASE WHEN ai_used = 1 THEN 1 ELSE 0 END) AS ai_triaged,
    SUM(CASE WHEN human_override = 1 THEN 1 ELSE 0 END) AS overrides,
    ROUND(
        100.0 * SUM(CASE WHEN human_override = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN ai_used = 1 THEN 1 ELSE 0 END), 0),
        1
    ) AS override_rate_pct
FROM support_tickets
GROUP BY category
ORDER BY override_rate_pct DESC;

-- 3) Operational outcome: average resolution time by issue type.
SELECT
    category,
    COUNT(*) AS resolved_tickets,
    ROUND(AVG(resolution_hours), 1) AS avg_resolution_hours
FROM support_tickets
WHERE status = 'Resolved'
GROUP BY category
ORDER BY avg_resolution_hours DESC;

-- 4) Backlog: high-risk unresolved work that needs attention.
SELECT
    ticket_id,
    market,
    channel,
    category,
    priority,
    status
FROM support_tickets
WHERE status <> 'Resolved'
  AND priority IN ('Urgent', 'High')
ORDER BY
    CASE priority WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 ELSE 3 END,
    ticket_id;

-- 5) Channel mix: useful for rollout sequencing and support workflow design.
SELECT
    channel,
    COUNT(*) AS tickets,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS share_pct
FROM support_tickets
GROUP BY channel
ORDER BY tickets DESC;
