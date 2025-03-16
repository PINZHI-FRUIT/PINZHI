package com.llw.imagediscerndemo.adapter;

import android.util.Log;
import android.widget.TextView;

import androidx.annotation.Nullable;

import com.chad.library.adapter.base.BaseQuickAdapter;
import com.chad.library.adapter.base.BaseViewHolder;
import com.llw.imagediscerndemo.R;
import com.llw.imagediscerndemo.model.GetDiscernResultResponse;

import java.util.List;

/**
 * 识别结果列表适配器
 */
public class DiscernResultAdapter extends BaseQuickAdapter<String, BaseViewHolder> {
    public DiscernResultAdapter(int layoutResId, @Nullable List<String> data) {
        super(layoutResId, data);
    }

    @Override
    protected void convert(BaseViewHolder helper, String fruitLabel) {
        // 在这里根据需要设置 tv_fruit_label 的文本
        // 获取 ViewHolder 中的 TextView 对象
        TextView tvFruitLabel = helper.getView(R.id.tv_fruit_label);
        // 检查 TextView 对象是否为空
        if (tvFruitLabel != null) {
            // 设置 TextView 的文本
            tvFruitLabel.setText(fruitLabel);
        }else{
            // 打印错误信息
            System.out.println("tvFruitLabel is null");
            Log.d(TAG,"没有tvFruitLabel");
        }
    }
}