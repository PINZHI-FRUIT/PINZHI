package com.llw.imagediscerndemo.util;

/**
 * Base64 工具类
 */
public class Base64Util {
    private static final char last2byte = (char) Integer.parseInt("00000011", 2);
    private static final char last4byte = (char) Integer.parseInt("00001111", 2);
    private static final char last6byte = (char) Integer.parseInt("00111111", 2);
    private static final char lead6byte = (char) Integer.parseInt("11111100", 2);
    private static final char lead4byte = (char) Integer.parseInt("11110000", 2);
    private static final char lead2byte = (char) Integer.parseInt("11000000", 2);
    private static final char[] encodeTable = new char[]{'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '/'};

    /**
     * Base64Util类的构造函数，用于创建Base64Util对象。
     */
    public Base64Util() {
    }

    /**
     * 将字节数组转换为Base64编码的字符串
     *
     * @param from 字节数组
     * @return Base64编码的字符串
     */
    public static String encode(byte[] from) {
        // 初始化StringBuilder对象，大小约为from.length的1.34倍再加3
        StringBuilder to = new StringBuilder((int) ((double) from.length * 1.34D) + 3);
        int num = 0;
        char currentByte = 0;

        int i;
        for (i = 0; i < from.length; ++i) {
            // 循环处理每个字节的8位
            for (num %= 8; num < 8; num += 6) {
                switch (num) {
                    // 处理字节的第1、3、5、7位
                    case 0:
                        // 取字节的高6位
                        currentByte = (char) (from[i] & lead6byte);
                        // 右移2位
                        currentByte = (char) (currentByte >>> 2);
                    case 1:
                    case 3:
                    case 5:
                    default:
                        break;
                    // 处理字节的第2位
                    case 2:
                        // 取字节的低6位
                        currentByte = (char) (from[i] & last6byte);
                        break;
                    // 处理字节的第4位
                    case 4:
                        // 取字节的低4位
                        currentByte = (char) (from[i] & last4byte);
                        // 左移2位
                        currentByte = (char) (currentByte << 2);
                        // 如果还有下一个字节
                        if (i + 1 < from.length) {
                            // 取下一个字节的高2位并右移6位
                            currentByte = (char) (currentByte | (from[i + 1] & lead2byte) >>> 6);
                        }
                        break;
                    // 处理字节的第6位
                    case 6:
                        // 取字节的低2位
                        currentByte = (char) (from[i] & last2byte);
                        // 左移4位
                        currentByte = (char) (currentByte << 4);
                        // 如果还有下一个字节
                        if (i + 1 < from.length) {
                            // 取下一个字节的高4位并右移4位
                            currentByte = (char) (currentByte | (from[i + 1] & lead4byte) >>> 4);
                        }
                }

                // 将当前字节对应的编码字符添加到StringBuilder中
                to.append(encodeTable[currentByte]);
            }
        }

        // 如果to的长度不是4的倍数，则在末尾添加等号以补齐
        if (to.length() % 4 != 0) {
            for (i = 4 - to.length() % 4; i > 0; --i) {
                to.append("=");
            }
        }

        // 返回编码后的字符串
        return to.toString();
    }

}
