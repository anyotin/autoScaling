#----------------------------------------
# ALBの作成
#----------------------------------------
resource "aws_lb" "auto-scaling" {
  name               = "tnn-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.auto-scaling-lb.id]
  subnets            = [aws_subnet.auto-scaling-lb-a.id,aws_subnet.auto-scaling-lb-c.id]

//  access_logs {
//    bucket  = aws_s3_bucket.lb_logs.id
//    prefix  = "test-lb"
//    enabled = true
//  }

  tags = {
    Environment = "auto-scaling"
  }
}

#----------------------------------------
# ALBターゲットグループの作成
#----------------------------------------
resource "aws_alb_target_group" "auto-scaling" {
  name     = "tnn-alb-tg"
  port     = 80
  protocol = "HTTP"
  deregistration_delay = 30 // デフォルトは300秒
  vpc_id   = aws_vpc.auto-scaling.id

  health_check {
    interval            = 30
    path                = "/index.html"
    port                = 80
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
    matcher             = 200
  }
}

#----------------------------------------
# ALBターゲットグループアタッチの作成
#----------------------------------------
resource "aws_alb_target_group_attachment" "tnn_alb_att" {
  target_group_arn = aws_alb_target_group.auto-scaling.arn
  target_id        = aws_instance.auto-scaling-web.id
  port             = 80
}

#----------------------------------------
# ALBリスナーの作成
#----------------------------------------
resource "aws_alb_listener" "tnn_alb_li" {
  load_balancer_arn = aws_lb.auto-scaling.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.auto-scaling.arn
    type             = "forward"
  }
}
