package com.llw.imagediscerndemo;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.FileProvider;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.Toast;

import com.bumptech.glide.Glide;
import com.bumptech.glide.request.target.CustomTarget;
import com.bumptech.glide.request.transition.Transition;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.llw.imagediscerndemo.adapter.DiscernResultAdapter;
import com.llw.imagediscerndemo.model.GetDiscernResultResponse;
import com.llw.imagediscerndemo.model.GetTokenResponse;
import com.llw.imagediscerndemo.network.ApiService;
import com.llw.imagediscerndemo.network.NetCallBack;
import com.llw.imagediscerndemo.network.ServiceGenerator;
import com.llw.imagediscerndemo.util.Base64Util;
import com.llw.imagediscerndemo.util.Constant;
import com.llw.imagediscerndemo.util.FileUtil;
import com.llw.imagediscerndemo.util.SPUtils;
import com.tbruyelle.rxpermissions2.RxPermissions;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Objects;

import retrofit2.Call;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    /**
     * 打开相册
     */
    private static final int OPEN_ALBUM_CODE = 100;
    /**
     * 打开相机
     */
    private static final int TAKE_PHOTO_CODE = 101;
    /**
     * Api服务
     */
    private ApiService service;
    /**
     * 鉴权Toeken
     */
    private String accessToken;
    /**
     * 显示图片
     */
    private ImageView ivPicture;
    /**
     * 进度条
     */
    private ProgressBar pbLoading;
    /**
     * 底部弹窗
     */
    private BottomSheetDialog bottomSheetDialog;
    /**
     * 弹窗视图
     */
    private View bottomView;

    String apiUrl = "http://10.252.118.223:5000/upload/"; // API 地址
    private RxPermissions rxPermissions;

    private File outputImage;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // 设置当前Activity的布局为activity_main
        setContentView(R.layout.activity_main);

        // 获取图片显示控件
        ivPicture = findViewById(R.id.iv_picture);
        // 获取加载进度条控件
        pbLoading = findViewById(R.id.pb_loading);
        // 创建底部弹窗实例
        bottomSheetDialog = new BottomSheetDialog(this);
        // 加载底部弹窗的布局
        bottomView = getLayoutInflater().inflate(R.layout.dialog_bottom, null);

        // 创建RxPermissions实例，用于处理动态权限请求
        rxPermissions = new RxPermissions(this);

    }

    /**
     * 识别网络图片
     *
     * @param view
     */
    public void IdentifyWebPictures(View view) {
        // 显示加载进度条
        pbLoading.setVisibility(View.VISIBLE);

        // 设置图片URL
        String imgUrl = "https://pic3.zhimg.com/80/v2-8e355085242beb2ca2c9988d969ce9bf_qhd.jpg";

        // 使用Glide库加载图片并转换为Base64字符串
        Glide.with(this)
                .asBitmap()
                .load(imgUrl)
                .into(new CustomTarget<Bitmap>() {
                    @Override
                    public void onResourceReady(@NonNull Bitmap resource, @Nullable Transition<? super Bitmap> transition) {
                        // 将Bitmap转换为Base64字符串
                        ByteArrayOutputStream baos = new ByteArrayOutputStream();
                        resource.compress(Bitmap.CompressFormat.JPEG, 100, baos);
                        byte[] imageBytes = baos.toByteArray();
                        String imageBase64 = Base64.encodeToString(imageBytes, Base64.DEFAULT);

                        // 使用Glide库显示图片
                        Glide.with(MainActivity.this).load(resource).into(ivPicture);

                        // 显示正在识别的消息
                        showMsg("图像识别中");

                        // 调用图像识别方法
                        ImageDiscern(apiUrl, imageBase64);
                    }

                    @Override
                    public void onLoadCleared(@Nullable Drawable placeholder) {
                        // 图像加载被取消时的操作（可选）
                    }
                });
    }
    /**
     * 图像识别请求(by hjw)
     *
     * @param apiUrl       api请求地址
     * @param imageBase64 图片Base64
     */
    private void ImageDiscern(String apiUrl, String imageBase64){
        // 创建一个新的 Retrofit 实例，使用指定的 API 请求地址
        ApiService customService = ServiceGenerator.createCustomService(ApiService.class, apiUrl);

        // 根据参数选择不同的方式进行图像识别
        if (imageBase64 != null) {
            customService.getDiscernResult(imageBase64).enqueue(new NetCallBack<GetDiscernResultResponse>() {
                @Override
                public void onSuccess(Call<GetDiscernResultResponse> call, Response<GetDiscernResultResponse> response) {
                    GetDiscernResultResponse result = response.body();
                    if (result != null) {
                        // 获取识别结果
                        String fruitLabel = result.getFruit_label();
                        Log.d(TAG, "成功: 图像识别请求成功，识别结果: " + fruitLabel);
                        // 显示识别结果
                        showDiscernResult(fruitLabel);
                    } else {
                        showMsg("没get到反馈的result");
                        Log.d(TAG, "没get到反馈的result");
                    }
                }

                @Override
                public void onFailed(String errorStr) {
                    Log.e(TAG, "Image Discern request failed, error: " + errorStr);
                    showMsg("未获得相应的识别结果");
                }
            });
        } else {
            showMsg("图片数据为空");
        }
    }


    /**
     * 显示识别的结果
     *
     * @param fruitLabel 识别结果字符串
     */
    private void showDiscernResult(String fruitLabel) {
        // 创建一个包含识别结果的列表
        List<String> fruitLabels = new ArrayList<>();
        fruitLabels.add(fruitLabel);

        // 设置底部弹窗的内容视图
        bottomSheetDialog.setContentView(bottomView);
        // 设置底部弹窗的背景颜色为透明
        bottomSheetDialog.getWindow().findViewById(R.id.design_bottom_sheet).setBackgroundColor(Color.TRANSPARENT);
        // 获取识别结果列表的 RecyclerView
        RecyclerView rvResult = bottomView.findViewById(R.id.rv_result);
        // 创建识别结果列表的适配器
        DiscernResultAdapter adapter = new DiscernResultAdapter(R.layout.item_result_rv, fruitLabels);
        // 设置 RecyclerView 的布局管理器
        rvResult.setLayoutManager(new LinearLayoutManager(this));
        // 设置 RecyclerView 的适配器
        rvResult.setAdapter(adapter);
        // 隐藏加载进度条
        pbLoading.setVisibility(View.GONE);
        // 显示底部弹窗
        bottomSheetDialog.show();
    }

    /**
     * 识别相册图片
     *
     * @param view
     */
    @SuppressLint("CheckResult")
    public void IdentifyAlbumPictures(View view) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            rxPermissions.request(
                    Manifest.permission.READ_EXTERNAL_STORAGE,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    .subscribe(grant -> {
                        if (grant) {
                            //获得权限
                            openAlbum();
                        } else {
                            showMsg("未获取到权限");
                        }
                    });
        } else {
            openAlbum();
        }
    }

    /**
     * 识别拍照图片
     *
     * @param view
     */
    @SuppressLint("CheckResult")
    public void IdentifyTakePhotoImage(View view) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            rxPermissions.request(
                            Manifest.permission.CAMERA)
                    .subscribe(grant -> {
                        if (grant) {
                            // 获得权限后打开相机
                            turnOnCamera();
                        } else {
                            showMsg("未获取到权限");
                        }
                    });
        } else {
            turnOnCamera();
        }
    }

    /**
     * 打开相机
     */
    private void turnOnCamera() {
        SimpleDateFormat timeStampFormat = new SimpleDateFormat("HH_mm_ss");
        String filename = timeStampFormat.format(new Date());
        // 创建File对象
        outputImage = new File(getExternalCacheDir(), "takePhoto" + filename + ".jpg");
        Uri imageUri;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            imageUri = FileProvider.getUriForFile(this,
                    "com.llw.imagediscerndemo.fileprovider", outputImage);
        } else {
            imageUri = Uri.fromFile(outputImage);
        }
        // 打开相机
        Intent intent = new Intent();
        intent.setAction(MediaStore.ACTION_IMAGE_CAPTURE);
        intent.putExtra(MediaStore.EXTRA_OUTPUT, imageUri);
        startActivityForResult(intent, TAKE_PHOTO_CODE);
    }

    /**
     * 接收相机拍摄后返回的图片
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == TAKE_PHOTO_CODE && resultCode == RESULT_OK) {
            // 拍照成功，进行图像识别
            if (outputImage != null) {
                String imagePath = outputImage.getAbsolutePath();
                //通过图片路径显示图片
                Glide.with(this).load(imagePath).into(ivPicture);
                //按字节读取文件
                byte[] imgData = new byte[0];
                try {
                    imgData = FileUtil.readFileByBytes(imagePath);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                //字节转Base64
                String imageBase64 = Base64Util.encode(imgData);
                //图像识别
                ImageDiscern(apiUrl, imageBase64);
            } else {
                showMsg("获取拍摄的图片失败");
            }
        }
    }



    /**
     * 打开相册
     */
    private void openAlbum() {
        Intent intent = new Intent();
        intent.setAction(Intent.ACTION_PICK);
        intent.setType("image/*");
        startActivityForResult(intent, OPEN_ALBUM_CODE);
    }


    /**
     * Toast提示
     *
     * @param msg 内容
     */
    private void showMsg(String msg) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show();
    }

    /**
     * 本地图片识别
     */
    private void localImageDiscern(String imagePath) {
        try {
            //通过图片路径显示图片
            Glide.with(this).load(imagePath).into(ivPicture);
            //按字节读取文件
            byte[] imgData = FileUtil.readFileByBytes(imagePath);
            //字节转Base64
            String imageBase64 = Base64Util.encode(imgData);
            //图像识别
            ImageDiscern(apiUrl, imageBase64);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}


