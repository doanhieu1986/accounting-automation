# Mục tiêu dự án

Đây là dự án thực hiện chiết xuất thông tin tự động từ các chứng từ kế toán như hóa đơn, phiếu thu, phiếu chi, giấy báo nợ, giấy báo có ...

1. Nguồn dữ liệu là các File PDF do người dùng kéo vào, sau đó hệ thống sẽ tự động chiết xuất thông tin từ các file PDF này. 

2. Output cần có 1 file Excel chứa các thông tin đã chiết xuất, file Excel này sẽ có các cột sau:
    - Số giao dịch
    - Số tham chiếu
    - Ngày giao dịch
    - Tên tài khoản (người chuyển tiền hoặc người nhận tiền nhưng không phải là tài khoản ngân hàng của công ty)
    - Số tài khoản (người chuyển tiền hoặc người nhận tiền nhưng không phải là tài khoản ngân hàng của công ty)
    - Nội dung thanh toán
    