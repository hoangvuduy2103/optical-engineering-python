import math

def calculate_initial_optical_params(
    efl=None,            # Tiêu cự hiệu dụng Effective Focal Length (mm)
    f_number=None,       # Khai báo F-number (F/#)
    fov_deg=None,        # Trường nhìn toàn phần Full Field of View (độ)
    sensor_w=None,       # Chiều rộng cảm biến hoặc đường kính cảm biến tròn (mm)
    sensor_h=None,       # Chiều cao cảm biến (mm)
    object_dist=None     # Khoảng cách từ vật đến thấu kính (mm), âm nếu vật thật (vd: -1000)
):
    """
    Tự động tính toán bộ thông số cấu tạo ban đầu cho hệ quang học.
    """
    results = {}
    
    # 1. Tính kích thước đường chéo/đường kính cảm biến (Sensor Diagonal/Diameter)
    if sensor_w is not None and sensor_h is not None:
        sensor_diag = math.sqrt(sensor_w**2 + sensor_h**2)
        results['1. Đường chéo cảm biến (mm)'] = sensor_diag
    elif sensor_w is not None:
        sensor_diag = sensor_w  # Trường hợp cảm biến tròn (như ống NVD 18mm)
        results['1. Đường kính cảm biến (mm)'] = sensor_diag
    else:
        sensor_diag = None

    # 2. Tính Tiêu cự EFL (nếu chưa biết) dựa trên FOV và Kích thước cảm biến
    if efl is None and fov_deg is not None and sensor_diag is not None:
        half_fov_rad = math.radians(fov_deg / 2)
        efl = (sensor_diag / 2) / math.tan(half_fov_rad)
        results['2. Tiêu cự tính toán EFL (mm)'] = efl
    elif efl is not None:
        results['2. Tiêu cự khai báo EFL (mm)'] = efl

    # 3. Tính Đường kính đồng tử vào (Entrance Pupil Diameter - EPD)
    if efl is not None and f_number is not None:
        epd = efl / f_number
        results['3. Đường kính đồng tử vào EPD (mm)'] = epd
    else:
        epd = None

    # 4. Tính Chiều cao ảnh cận trục (Paraxial Image Height h') & Nửa góc trường (Half FOV)
    if efl is not None and fov_deg is not None:
        half_fov_rad = math.radians(fov_deg / 2)
        h_prime = efl * math.tan(half_fov_rad)
        results['4. Chiều cao ảnh cận trục h\' (mm)'] = h_prime
        results['5. Nửa góc trường nhìn Half-FOV (độ)'] = fov_deg / 2

    # 5. Tính Khẩu độ số (NA) & Góc tia biên cận trục (Marginal Ray Angle u')
    if f_number is not None:
        na_image = math.sin(math.atan(1 / (2 * f_number)))
        results['6. Khẩu độ số NA (Vật vô cực)'] = na_image
        
        if epd is not None and efl is not None:
            u_prime_rad = - (epd / 2) / efl  # u' = -1 / (2 * F/#)
            results['7. Góc tia biên u\' (rad) [Dùng cho Marginal Ray Solve]'] = u_prime_rad
            results['7. Góc tia biên u\' (độ)'] = math.degrees(u_prime_rad)

    # 6. Tính toán cho Khoảng cách vật hữu hạn (Finite Object Distance)
    if efl is not None and object_dist is not None and object_dist < 0:
        s = object_dist
        f = efl
        # Phương trình tạo ảnh cận trục: 1/s' - 1/s = 1/f
        inv_s_prime = (1 / f) + (1 / s)
        if inv_s_prime != 0:
            s_prime = 1 / inv_s_prime
            m = s_prime / s
            working_f_num = (1 - m) * f_number
            working_na = 1 / (2 * working_f_num)
            
            results['8. Khoảng cách ảnh s\' (mm)'] = s_prime
            results['9. Độ phóng đại ngang (m)'] = m
            results['10. Working F/# (Khẩu độ làm việc)'] = working_f_num
            results['11. Working NA'] = working_na

    return results
