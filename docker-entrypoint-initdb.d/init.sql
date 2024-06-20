CREATE TABLE IF NOT EXISTS "citro_analytics"."transactions" (
    transactionId String,
    transactionTimeUtc DateTime64(6, 'UTC'),
    category String,
    transactionType String,
    counterpartName String,
    amount Decimal256(2)
) 
ENGINE ReplacingMergeTree
PARTITION BY toYYYYMM(transactionTimeUtc) 
PRIMARY KEY transactionId

