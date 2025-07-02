-- 创建生成随机19位银行卡号的函数
CREATE OR REPLACE FUNCTION generate_random_card_id()
RETURNS VARCHAR(19) AS $$
DECLARE
    card_id VARCHAR(19);
    exists_count INTEGER;
BEGIN
    LOOP
        -- 生成19位随机数字作为银行卡号
        -- 前6位是银行标识码 (固定为 622222)
        -- 中间12位是随机数字
        -- 最后1位是校验位 (简化处理，这里也用随机数)
        card_id := '622222' || 
                  LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0') || 
                  LPAD(FLOOR(RANDOM() * 1000000)::TEXT, 6, '0') || 
                  FLOOR(RANDOM() * 10)::TEXT;
        
        -- 检查生成的卡号是否已存在
        SELECT COUNT(*) INTO exists_count FROM bank_app_cardinfo WHERE "cardID" = card_id;
        
        -- 如果卡号不存在，则退出循环
        IF exists_count = 0 THEN
            EXIT;
        END IF;
    END LOOP;
    
    RETURN card_id;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器函数，在插入新银行卡记录前自动生成卡号
CREATE OR REPLACE FUNCTION auto_generate_card_id()
RETURNS TRIGGER AS $$
BEGIN
    -- 如果没有提供卡号或卡号为空，则自动生成
    IF NEW."cardID" IS NULL OR NEW."cardID" = '' THEN
        NEW."cardID" := generate_random_card_id();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器，在插入前调用触发器函数
DROP TRIGGER IF EXISTS trigger_auto_generate_card_id ON bank_app_cardinfo;
CREATE TRIGGER trigger_auto_generate_card_id
BEFORE INSERT ON bank_app_cardinfo
FOR EACH ROW
EXECUTE FUNCTION auto_generate_card_id();