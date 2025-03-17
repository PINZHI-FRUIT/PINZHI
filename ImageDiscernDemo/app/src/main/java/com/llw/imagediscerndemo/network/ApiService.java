package com.llw.imagediscerndemo.network;

import com.llw.imagediscerndemo.model.GetDiscernResultResponse;
import com.llw.imagediscerndemo.model.GetTokenResponse;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Field;
import retrofit2.http.FormUrlEncoded;
import retrofit2.http.Headers;
import retrofit2.http.POST;

/**
 * API服务
 *
 * @author llw
 * @date 2021/4/1 17:48
 */
public interface ApiService {

    /**
     * 获取鉴权认证Token
     *
     * @param grant_type 类型
     * @param client_id API Key
     * @param client_secret Secret Key
     * @return 返回GetTokenResponse对象
     */
    // 使用@FormUrlEncoded注解，表示该方法使用表单方式进行数据编码
    @FormUrlEncoded
    // 使用@POST注解，表示该方法使用POST请求方式发送数据
    @POST("/oauth/2.0/token")
    // 返回一个Call<GetTokenResponse>类型的对象，用于发送请求并获取响应
    Call<GetTokenResponse> getToken(
        @Field("grant_type") String grant_type,
        @Field("client_id") String client_id,
        @Field("client_secret") String client_secret
        // @Field("grant_type")注解表示将grant_type参数以表单字段的形式发送到服务器
        // @Field("client_id")注解表示将client_id参数以表单字段的形式发送到服务器
        // @Field("client_secret")注解表示将client_secret参数以表单字段的形式发送到服务器
    );


    /**
     * 获取图像识别结果
     *
     * @param accessToken 获取鉴权认证Token
     * @param image 图片base64
     * @param url 网络图片Url
     * @return JsonObject
     */
    // 使用FormUrlEncoded注解表示请求参数将进行表单编码
    @FormUrlEncoded
    // 使用POST注解表示这是一个POST请求
    @POST("/rest/2.0/image-classify/v2/advanced_general")
    // 设置请求头，指定Content-Type为application/x-www-form-urlencoded，并指定字符集为utf-8
    @Headers("Content-Type:application/x-www-form-urlencoded; charset=utf-8")
    // 定义一个名为getDiscernResult的方法，该方法接收三个参数：accessToken、image和url
    Call<GetDiscernResultResponse> getDiscernResult(
        @Field("access_token") String accessToken,
        @Field("image") String image,
        @Field("url") String url);
        // 使用@Field注解表示将参数名设置为"access_token"，参数值为accessToken
        // 使用@Field注解表示将参数名设置为"image"，参数值为image
        // 使用@Field注解表示将参数名设置为"url"，参数值为url
        @FormUrlEncoded
        @POST("/upload") // 修改为您的 Flask API 的上传地址
        @Headers("Content-Type:application/x-www-form-urlencoded; charset=utf-8")
        Call<GetDiscernResultResponse> getDiscernResult(
                @Field("image") String imageBase64
        );
    @FormUrlEncoded
    @POST("/upload") // 修改为您的 Flask API 的上传地址
    @Headers("Content-Type:application/x-www-form-urlencoded; charset=utf-8")
    Call<GetDiscernResultResponse> getDiscernResultByUrl(
            @Field("url") String imgUrl
    );

    @FormUrlEncoded
    @POST("/upload") // 修改为您的 Flask API 的上传地址
    @Headers("Content-Type:application/x-www-form-urlencoded; charset=utf-8")
    Call<GetDiscernResultResponse> getDiscernResultByBase64(
            @Field("image") String imageBase64
    );
}
