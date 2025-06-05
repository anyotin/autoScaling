#----------------------------------------
# ALBの作成
#----------------------------------------
resource "aws_lb" "eggplant" {
  name               = "tnn-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.eggplant-lb.id]
  subnets            = [aws_subnet.eggplant-lb-a.id,aws_subnet.eggplant-lb-c.id]

//  access_logs {
//    bucket  = aws_s3_bucket.lb_logs.id
//    prefix  = "test-lb"
//    enabled = true
//  }

  tags = {
    Environment = "eggplant"
  }
}

#----------------------------------------
# ALBターゲットグループの作成
#----------------------------------------
resource "aws_alb_target_group" "eggplant" {
  name     = "eggplant"
  port     = 80
  protocol = "HTTP"
  deregistration_delay = 30 // デフォルトは300秒
  vpc_id   = aws_vpc.eggplant.id

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
# ALBターゲットグループの作成
#----------------------------------------
resource "aws_alb_target_group" "eggplant-auto-scaling" {
  name     = "eggplant"
  port     = 80
  protocol = "HTTP"
  deregistration_delay = 30 // デフォルトは300秒
  vpc_id   = aws_vpc.eggplant.id

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
resource "aws_alb_target_group_attachment" "eggplant" {
  target_group_arn = aws_alb_target_group.eggplant.arn
  target_id        = aws_instance.eggplant.id
  port             = 80
}

#----------------------------------------
# ALBリスナーの作成
#----------------------------------------
resource "aws_alb_listener" "eggplant" {
  load_balancer_arn = aws_lb.eggplant.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.eggplant.arn
    type             = "forward"
  }
}
