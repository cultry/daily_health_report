# 某双一流大学健康打卡捷径

## 打卡教程

1. 访问地址 [获取打卡列表](http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do)，返回的json中<code>data</code>字段为相应的打卡列表
2. 根据日期找到待打卡的项目对应的<code>WID</code>，未打卡的项中会带有<code>"TBZT": "0"</code>的项
3. 根据下面的规则构造打卡请求地址
4. 访问**步骤3**构造的地址得到成功的返回请求

```php+HTML
https://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?WID={步骤2中获取到的WID}&CURR_LOCATION={打卡地址，例如：中国江苏省南京市栖霞区仙林大道}&IS_TWZC=1&IS_HAS_JKQK=1&JRSKMYS=1&JZRJRSKMYS=1 

#理论上只需要修改WID以及打卡地址，注意要去掉地址中的花括号
```

## 免责声明

该打卡方法仅供学习Web协议使用，请勿用于任何违规违法用途，造成任何后果与作者无关！
