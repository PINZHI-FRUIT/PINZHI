package com.llw.imagediscerndemo.model;

import java.util.List;

/**
 * 获取识别结果响应实体
 *
 * @author llw
 * @date 2021/4/2 16:30
 */
public class GetDiscernResultResponse {
    private String message;
    private String fruit_label;

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getFruit_label() {
        return fruit_label;
    }

    public void setFruit_label(String fruit_label) {
        this.fruit_label = fruit_label;
    }

    public GetDiscernResultResponse(String message, String fruit_label) {
        this.message = message;
        this.fruit_label = fruit_label;
    }

    // 构造函数、getter和setter方法
}
