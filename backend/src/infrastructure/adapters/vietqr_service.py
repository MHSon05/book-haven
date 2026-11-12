"""
Infrastructure Adapter: VietQRService
Sinh mã VietQR động chuẩn ngân hàng MBBank phục vụ thanh toán trực tuyến tức thì.
"""
import os
import urllib.parse
from typing import Dict, Any

class VietQRService:
    def __init__(
        self,
        bank_id: str = None,
        account_no: str = None,
        account_name: str = None
    ):
        self.bank_id = bank_id or os.getenv("BANK_ID", "MB")
        self.account_no = account_no or os.getenv("BANK_ACCOUNT_NO", "0912345678")
        self.account_name = account_name or os.getenv("BANK_ACCOUNT_NAME", "NHA SACH BOOKHAVEN")

    def generate_payment_qr(self, order_id: str, amount: int) -> Dict[str, Any]:
        """
        Sinh URL hình ảnh VietQR động và thông tin chuyển khoản chuẩn xác.
        """
        memo = f"BOOKHAVEN {order_id}"
        encoded_memo = urllib.parse.quote(memo)
        encoded_name = urllib.parse.quote(self.account_name)

        # URL VietQR API chuẩn Napas QuickLink
        qr_image_url = (
            f"https://img.vietqr.io/image/{self.bank_id}-{self.account_no}-compact2.png"
            f"?amount={amount}&addInfo={encoded_memo}&accountName={encoded_name}"
        )

        return {
            "qr_image_url": qr_image_url,
            "qr_url": qr_image_url,
            "bank_id": self.bank_id,
            "bank_name": "Ngân hàng TMCP Quân Đội (MBBank)",
            "account_no": self.account_no,
            "account_name": self.account_name,
            "amount": amount,
            "order_id": order_id,
            "transfer_memo": memo
        }
