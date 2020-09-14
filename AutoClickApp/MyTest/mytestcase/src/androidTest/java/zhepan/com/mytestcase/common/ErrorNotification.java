package zhepan.com.mytestcase.common;

import android.app.Activity;
import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.view.View;

import zhepan.com.mytestcase.R;

public class ErrorNotification extends Activity {

    private static int id = 1;

    public void sendNotification() {
        NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        Notification notification = new Notification.Builder(this)
                .setSmallIcon(R.drawable.ic_launcher_foreground)//设置小图标
                .setContentTitle("这是标题")
                .setContentText("这是内容")
                .build();
        manager.notify(id++, notification);
    }

    public void cleanNotification(View view) {
        NotificationManager mNotificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        mNotificationManager.cancelAll();
        mNotificationManager.cancel(1);
    }
}
